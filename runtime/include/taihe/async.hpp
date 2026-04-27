/*
 * Copyright (c) 2026 Huawei Device Co., Ltd.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef TAIHE_ASYNC_HPP
#define TAIHE_ASYNC_HPP

#include <taihe/async.abi.h>
#include <taihe/common.hpp>
#include <taihe/expected.hpp>
#include <utility>

namespace taihe {
template<typename Result>
struct async_context {
private:
    union ResultBuffer {
        ResultBuffer()
        {
        }

        ~ResultBuffer()
        {
        }

        Result result;
    };

    uint32_t ref_count;
    uint8_t handler_guard;
    uint8_t result_guard;
    uint8_t handshake_flags;
    uint8_t reserved;

    void (*process_handler_ptr)(TAsyncHandlerStorage *storage_ptr, Result *result_ptr);
    void (*cleanup_handler_ptr)(TAsyncHandlerStorage *storage_ptr);
    TAsyncHandlerStorage storage;
    ResultBuffer buffer;

public:
    using result_type = Result;

    async_context(async_context const &) = delete;
    async_context &operator=(async_context const &) = delete;
    async_context(async_context &&) = delete;
    async_context &operator=(async_context &&) = delete;

    explicit async_context(uint32_t ref_count)
        : ref_count(ref_count)
        , handler_guard(TH_ASYNC_CONTEXT_HANDLER_NONE)
        , result_guard(TH_ASYNC_CONTEXT_RESULT_NONE)
        , handshake_flags(TH_ASYNC_HANDSHAKE_NONE)
        , reserved(0)
        , process_handler_ptr(nullptr)
        , cleanup_handler_ptr(nullptr)
    {
    }

    void inc_ref()
    {
        __atomic_fetch_add(&ref_count, 1, __ATOMIC_ACQ_REL);
    }

    bool dec_ref()
    {
        return __atomic_sub_fetch(&ref_count, 1, __ATOMIC_ACQ_REL) == 0;
    }

private:
    // Atomically claims the result-emplacement slot. Returns true on first claim
    // (lock acquired); false means the result was already set — a programming error.
    bool try_lock_result()
    {
        uint8_t prev = __atomic_fetch_or(&result_guard, TH_ASYNC_CONTEXT_RESULT_LOCKED, __ATOMIC_ACQ_REL);
        return (prev & TH_ASYNC_CONTEXT_RESULT_LOCKED) == 0;
    }

    // Atomically claims the handler-registration slot. Returns true on first claim
    // (lock acquired); false means the handler was already set — a programming error.
    bool try_lock_handler()
    {
        uint8_t prev = __atomic_fetch_or(&handler_guard, TH_ASYNC_CONTEXT_HANDLER_LOCKED, __ATOMIC_ACQ_REL);
        return (prev & TH_ASYNC_CONTEXT_HANDLER_LOCKED) == 0;
    }

    // Sets HANDLER_READY in handshake_flags. Returns true if RESULT_READY was
    // already set, meaning this side arrived second and must dispatch the handler.
    bool notify_handler_ready()
    {
        uint8_t prev = __atomic_fetch_or(&handshake_flags, TH_ASYNC_HANDSHAKE_HANDLER_READY, __ATOMIC_ACQ_REL);
        return (prev & TH_ASYNC_HANDSHAKE_RESULT_READY) != 0;
    }

    // Sets RESULT_READY in handshake_flags. Returns true if HANDLER_READY was
    // already set, meaning this side arrived second and must dispatch the handler.
    bool notify_result_ready()
    {
        uint8_t prev = __atomic_fetch_or(&handshake_flags, TH_ASYNC_HANDSHAKE_RESULT_READY, __ATOMIC_ACQ_REL);
        return (prev & TH_ASYNC_HANDSHAKE_HANDLER_READY) != 0;
    }

    bool is_result_ready() const
    {
        return (handshake_flags & TH_ASYNC_HANDSHAKE_RESULT_READY) != 0;
    }

    bool is_handler_ready() const
    {
        return (handshake_flags & TH_ASYNC_HANDSHAKE_HANDLER_READY) != 0;
    }

    void process_handler()
    {
        process_handler_ptr(&storage, &buffer.result);
    }

    void cleanup_handler()
    {
        cleanup_handler_ptr(&storage);
    }

public:
    template<typename... Args>
    bool try_emplace_result(Args &&...args)
    {
        if (!try_lock_result()) {
            return false;
        }
        new (&buffer.result) Result(std::forward<Args>(args)...);

        if (notify_result_ready()) {
            process_handler();
        }
        return true;
    }

    template<typename... Args>
    void emplace_result(Args &&...args)
    {
        TH_ASSERT(try_emplace_result(std::forward<Args>(args)...), "Result has already been set");
    }

    template<typename SmallConstHandler, typename... Args>
    void emplace_handler(Args &&...args)
    {
        static_assert(sizeof(SmallConstHandler) <= sizeof(TAsyncHandlerStorage::buffer),
                      "Handler type is too large for small storage");

        TH_ASSERT(try_lock_handler(), "Handler has already been set");
        new (&storage.buffer) SmallConstHandler(std::forward<Args>(args)...);
        process_handler_ptr = [](TAsyncHandlerStorage *storage_ptr, Result *result_ptr) {
            (*reinterpret_cast<SmallConstHandler *>(&storage_ptr->buffer))(std::forward<Result>(*result_ptr));
        };
        cleanup_handler_ptr = [](TAsyncHandlerStorage *storage_ptr) {
            reinterpret_cast<SmallConstHandler *>(&storage_ptr->buffer)->~SmallConstHandler();
        };

        if (notify_handler_ready()) {
            process_handler();
        }
    }

    template<typename LargeMutableHandler, typename... Args>
    void new_handler(Args &&...args)
    {
        TH_ASSERT(try_lock_handler(), "Handler has already been set");
        storage.pointer = new LargeMutableHandler(std::forward<Args>(args)...);
        process_handler_ptr = [](TAsyncHandlerStorage *storage_ptr, Result *result_ptr) {
            (*reinterpret_cast<LargeMutableHandler *>(storage_ptr->pointer))(std::forward<Result>(*result_ptr));
        };
        cleanup_handler_ptr = [](TAsyncHandlerStorage *storage_ptr) {
            delete reinterpret_cast<LargeMutableHandler *>(storage_ptr->pointer);
        };

        if (notify_handler_ready()) {
            process_handler();
        }
    }

    ~async_context()
    {
        if (is_result_ready()) {
            buffer.result.~Result();
        }
        if (is_handler_ready()) {
            cleanup_handler();
        }
    }
};

template<typename Result>
class completer;

template<typename Result>
class future;

template<typename Result>
std::pair<completer<Result>, future<Result>> make_async_pair();

template<typename Result>
class completer {
public:
    using result_type = Result;

    async_context<Result> *m_ctx;

    explicit completer(async_context<Result> *ctx) : m_ctx(ctx)
    {
    }

    friend std::pair<completer<Result>, future<Result>> make_async_pair<Result>();

    completer(completer const &other) : m_ctx(other.m_ctx)
    {
        if (m_ctx) {
            m_ctx->inc_ref();
        }
    }

    completer(completer &&other) : m_ctx(other.m_ctx)
    {
        other.m_ctx = nullptr;
    }

    completer &operator=(completer other)
    {
        std::swap(this->m_ctx, other.m_ctx);
        return *this;
    }

    ~completer()
    {
        if (m_ctx && m_ctx->dec_ref()) {
            delete m_ctx;
        }
    }

    template<typename... Args>
    bool try_complete(Args &&...args) const
    {
        return m_ctx->try_emplace_result(std::forward<Args>(args)...);
    }

    template<typename... Args>
    void complete(Args &&...args) const
    {
        m_ctx->emplace_result(std::forward<Args>(args)...);
    }
};

template<typename Result>
class future {
public:
    using result_type = Result;

    async_context<Result> *m_ctx;

    explicit future(async_context<Result> *ctx) : m_ctx(ctx)
    {
    }

    friend std::pair<completer<Result>, future<Result>> make_async_pair<Result>();

    future(future const &other) : m_ctx(other.m_ctx)
    {
        if (m_ctx) {
            m_ctx->inc_ref();
        }
    }

    future(future &&other) : m_ctx(other.m_ctx)
    {
        other.m_ctx = nullptr;
    }

    future &operator=(future other)
    {
        std::swap(this->m_ctx, other.m_ctx);
        return *this;
    }

    ~future()
    {
        if (m_ctx && m_ctx->dec_ref()) {
            delete m_ctx;
        }
    }

    template<typename Handler, typename... Args>
    void on_complete(Args &&...args) const
    {
        if constexpr (sizeof(Handler) <= sizeof(TAsyncHandlerStorage::buffer)) {
            m_ctx->template emplace_handler<Handler>(std::forward<Args>(args)...);
        } else {
            m_ctx->template new_handler<Handler>(std::forward<Args>(args)...);
        }
    }

    template<typename Handler>
    void on_complete(Handler &&handler) const
    {
        on_complete<Handler, Handler>(std::forward<Handler>(handler));
    }
};

template<typename Result>
std::pair<completer<Result>, future<Result>> make_async_pair()
{
    async_context<Result> *ctx = new async_context<Result>(2);
    return {
        completer<Result>(ctx),
        future<Result>(ctx),
    };
}

template<typename Result>
struct as_abi<completer<Result>> {
    using type = TCompleter;
};

template<typename Result>
struct as_abi<future<Result>> {
    using type = TFuture;
};

template<typename Result>
struct as_param<completer<Result>> {
    using type = completer<Result>;
};

template<typename Result>
struct as_param<future<Result>> {
    using type = future<Result>;
};

template<typename Result>
inline bool operator==(completer<Result> const &lhs, completer<Result> const &rhs)
{
    return lhs.m_ctx == rhs.m_ctx;
}

template<typename Result>
inline bool operator==(future<Result> const &lhs, future<Result> const &rhs)
{
    return lhs.m_ctx == rhs.m_ctx;
}
}  // namespace taihe

template<typename Result>
struct std::hash<taihe::completer<Result>> {
    std::size_t operator()(taihe::completer<Result> const &val) const
    {
        return std::hash<void *>()(val.m_ctx);
    }
};

template<typename Result>
struct std::hash<taihe::future<Result>> {
    std::size_t operator()(taihe::future<Result> const &val) const
    {
        return std::hash<void *>()(val.m_ctx);
    }
};

// Utils

namespace taihe {
template<typename Result, typename Func>
future<Result> make_future(Func &&func)
{
    auto [com, fut] = make_async_pair<Result>();
    func(std::move(com));
    return std::move(fut);
}

template<typename Result, typename... Args>
future<Result> make_ready_future(Args &&...args)
{
    auto [com, fut] = make_async_pair<Result>();
    std::move(com).complete(std::forward<Args>(args)...);
    return std::move(fut);
}

template<typename Result>
future<Result> make_ready_future(Result &&result)
{
    return make_ready_future<Result, Result>(std::forward<Result>(result));
}

template<typename Result, typename Handler, typename... Args>
completer<Result> make_callback_completer(Args &&...args)
{
    auto [com, fut] = make_async_pair<Result>();
    std::move(fut).template on_complete<Handler, Args...>(std::forward<Args>(args)...);
    return std::move(com);
}

template<typename Result, typename Handler>
completer<Result> make_callback_completer(Handler &&handler)
{
    return make_callback_completer<Result, Handler, Handler>(std::forward<Handler>(handler));
}
}  // namespace taihe

namespace taihe::__detail {
template<typename Result, typename Func>
struct __then_sync_adaptor {
    using result_type = Result;
    Func func;
};

template<typename Result, typename Func>
struct __then_returns_future_adaptor {
    using result_type = Result;
    Func func;
};

template<typename Result, typename Func>
struct __then_with_completer_adaptor {
    using result_type = Result;
    Func func;
};
}  // namespace taihe::__detail

namespace taihe {
template<typename Result, typename Func>
__detail::__then_sync_adaptor<Result, Func> then_sync(Func &&func)
{
    return __detail::__then_sync_adaptor<Result, Func> {std::forward<Func>(func)};
}

template<typename Result, typename Func>
__detail::__then_returns_future_adaptor<Result, Func> then_returns_future(Func &&func)
{
    return __detail::__then_returns_future_adaptor<Result, Func> {std::forward<Func>(func)};
}

template<typename Result, typename Func>
__detail::__then_with_completer_adaptor<Result, Func> then_with_completer(Func &&func)
{
    return __detail::__then_with_completer_adaptor<Result, Func> {std::forward<Func>(func)};
}

template<typename Last, typename Next, typename Func>
auto operator|(future<Last> old, __detail::__then_sync_adaptor<Next, Func> adaptor)
{
    auto [com, fut] = make_async_pair<Next>();
    std::move(old).on_complete([func = std::forward<Func>(adaptor.func), com = std::move(com)](Last &&result) mutable {
        std::move(com).complete(func(std::forward<Last>(result)));
    });
    return std::move(fut);
}

template<typename Last, typename Next, typename Func>
auto operator|(future<Last> old, __detail::__then_returns_future_adaptor<Next, Func> adaptor)
{
    auto [com, fut] = make_async_pair<Next>();
    std::move(old).on_complete([func = std::forward<Func>(adaptor.func), com = std::move(com)](Last &&result) mutable {
        func(std::forward<Last>(result)).on_complete([com = std::move(com)](Next &&next) mutable {
            std::move(com).complete(std::forward<Next>(next));
        });
    });
    return std::move(fut);
}

template<typename Last, typename Next, typename Func>
auto operator|(future<Last> old, __detail::__then_with_completer_adaptor<Next, Func> adaptor)
{
    auto [com, fut] = make_async_pair<Next>();
    std::move(old).on_complete([func = std::forward<Func>(adaptor.func), com = std::move(com)](Last &&result) mutable {
        func(std::forward<Last>(result), std::move(com));
    });
    return std::move(fut);
}
}  // namespace taihe

namespace taihe {
template<typename Result>
future<Result> race(std::initializer_list<future<Result>> olds)
{
    auto [com, fut] = make_async_pair<Result>();

    completer<Result> shared_com(std::move(com));

    for (auto const &old : olds) {
        std::move(old).on_complete([shared_com](Result &&result) mutable {
            std::move(shared_com).try_complete(std::forward<Result>(result));
        });
    }

    return std::move(fut);
}
}  // namespace taihe

#endif  // TAIHE_ASYNC_HPP
