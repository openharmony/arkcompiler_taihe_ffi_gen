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

namespace taihe {
template<typename Result>
struct async_context {
    union ResultBuffer {
        Result result;

        ResultBuffer()
        {
        }

        ~ResultBuffer()
        {
        }
    };

    uint32_t ref_count;
    uint32_t flags;

    TAsyncHandlerStorage storage;
    void (*process_handler_ptr)(TAsyncHandlerStorage *storage, Result *result_ptr);
    void (*cleanup_handler_ptr)(TAsyncHandlerStorage *storage);

    ResultBuffer buffer;

    async_context(async_context const &) = delete;
    async_context &operator=(async_context const &) = delete;
    async_context(async_context &&) = delete;
    async_context &operator=(async_context &&) = delete;

    explicit async_context(uint32_t ref_count)
        : ref_count(ref_count), flags(ASYNC_CONTEXT_NONE), process_handler_ptr(nullptr), cleanup_handler_ptr(nullptr)
    {
    }

    bool dec_ref()
    {
        return __atomic_sub_fetch(&ref_count, 1, __ATOMIC_ACQ_REL) == 0;
    }

    uint32_t set_flags(uint32_t new_flags)
    {
        return __atomic_or_fetch(&flags, new_flags, __ATOMIC_ACQ_REL);
    }

    void process_handler()
    {
        process_handler_ptr(&storage, &buffer.result);
    }

    void cleanup_handler()
    {
        cleanup_handler_ptr(&storage);
    }

    template<typename... Args>
    void emplace_result(Args &&...args)
    {
        TH_ASSERT(!(flags & ASYNC_CONTEXT_RESULT_SET), "Result is already being set");
        new (&buffer.result) Result(std::forward<Args>(args)...);

        uint32_t old_flags = set_flags(ASYNC_CONTEXT_RESULT_SET);
        if (old_flags & ASYNC_CONTEXT_HANDLER_SET) {
            process_handler();
        }
    }

    template<typename SmallConstHandler, typename... Args>
    void emplace_handler(Args &&...args)
    {
        static_assert(sizeof(SmallConstHandler) <= sizeof(TAsyncHandlerStorage::buf),
                      "Handler type is too large for small storage");
        TH_ASSERT(!(flags & ASYNC_CONTEXT_HANDLER_SET), "Handler is already being set");
        new (&storage.buf) SmallConstHandler(std::forward<Args>(args)...);
        process_handler_ptr = [](TAsyncHandlerStorage *storage, Result *result_ptr) {
            (*reinterpret_cast<SmallConstHandler *>(&storage->buf))(std::forward<Result>(*result_ptr));
        };
        cleanup_handler_ptr = [](TAsyncHandlerStorage *storage) {
            reinterpret_cast<SmallConstHandler *>(&storage->buf)->~SmallConstHandler();
        };

        uint32_t old_flags = set_flags(ASYNC_CONTEXT_HANDLER_SET);
        if (old_flags & ASYNC_CONTEXT_RESULT_SET) {
            process_handler();
        }
    }

    template<typename LargeMutableHandler, typename... Args>
    void new_handler(Args &&...args)
    {
        TH_ASSERT(!(flags & ASYNC_CONTEXT_HANDLER_SET), "Handler is already being set");
        storage.ptr = new LargeMutableHandler(std::forward<Args>(args)...);
        process_handler_ptr = [](TAsyncHandlerStorage *storage, Result *result_ptr) {
            (*reinterpret_cast<LargeMutableHandler *>(storage->ptr))(std::forward<Result>(*result_ptr));
        };
        cleanup_handler_ptr = [](TAsyncHandlerStorage *storage) {
            delete reinterpret_cast<LargeMutableHandler *>(storage->ptr);
        };

        uint32_t old_flags = set_flags(ASYNC_CONTEXT_HANDLER_SET);
        if (old_flags & ASYNC_CONTEXT_RESULT_SET) {
            process_handler();
        }
    }

    ~async_context()
    {
        if (flags & ASYNC_CONTEXT_RESULT_SET) {
            buffer.result.~Result();
        }
        if (flags & ASYNC_CONTEXT_HANDLER_SET) {
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
    async_context<Result> *m_ctx;

    explicit completer(async_context<Result> *ctx) : m_ctx(ctx)
    {
    }

    friend std::pair<completer<Result>, future<Result>> make_async_pair<Result>();

    completer(completer const &) = delete;

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
    void complete(Args &&...args) const
    {
        m_ctx->emplace_result(std::forward<Args>(args)...);
    }
};

template<typename Result>
class future {
public:
    async_context<Result> *m_ctx;

    explicit future(async_context<Result> *ctx) : m_ctx(ctx)
    {
    }

    friend std::pair<completer<Result>, future<Result>> make_async_pair<Result>();

    future(future const &) = delete;

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
        if constexpr (sizeof(Handler) <= sizeof(TAsyncHandlerStorage::buf)) {
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
inline bool operator==(completer<Result> lhs, completer<Result> rhs)
{
    return lhs.m_ctx == rhs.m_ctx;
}

template<typename Result>
inline bool operator==(future<Result> lhs, future<Result> rhs)
{
    return lhs.m_ctx == rhs.m_ctx;
}
}  // namespace taihe

template<typename Result>
struct std::hash<taihe::completer<Result>> {
    std::size_t operator()(taihe::completer<Result> val) const
    {
        return std::hash<void *>()(val.m_ctx);
    }
};

template<typename Result>
struct std::hash<taihe::future<Result>> {
    std::size_t operator()(taihe::future<Result> val) const
    {
        return std::hash<void *>()(val.m_ctx);
    }
};

// Utils

#include <condition_variable>
#include <mutex>
#include <optional>

namespace taihe {
template<typename Result>
Result wait(future<Result> fut)
{
    struct WaitContext {
        std::mutex mtx;
        std::condition_variable cv;
        std::optional<Result> waited;
    };

    struct WaitHandler {
        WaitContext &ctx;

        explicit WaitHandler(WaitContext &ctx) : ctx(ctx)
        {
        }

        void operator()(Result &&result) const
        {
            std::unique_lock<std::mutex> lock(ctx.mtx);
            ctx.waited.emplace(std::forward<Result>(result));
            ctx.cv.notify_all();
        }
    };

    WaitContext ctx;
    fut.template on_complete<WaitHandler>(ctx);

    std::unique_lock<std::mutex> lock(ctx.mtx);
    ctx.cv.wait(lock, [&ctx]() {
        return ctx.waited.has_value();
    });

    return std::move(ctx.waited.value());
}

template<typename Result>
Result race(std::initializer_list<future<Result>> futs)
{
    struct RaceContext {
        std::mutex mtx;
        std::condition_variable cv;
        std::optional<Result> waited;
    };

    struct RaceHandler {
        std::shared_ptr<RaceContext> ptr;

        explicit RaceHandler(std::shared_ptr<RaceContext> ptr) : ptr(ptr)
        {
        }

        void operator()(Result &&result) const
        {
            std::unique_lock<std::mutex> lock(ptr->mtx);
            if (!ptr->waited.has_value()) {
                ptr->waited.emplace(std::forward<Result>(result));
                ptr->cv.notify_all();
            }
        }
    };

    auto ptr = std::make_shared<RaceContext>();
    for (auto const &fut : futs) {
        fut.template on_complete<RaceHandler>(ptr);
    }

    std::unique_lock<std::mutex> lock(ptr->mtx);
    ptr->cv.wait(lock, [ptr = ptr.get()]() {
        return ptr->waited.has_value();
    });

    return std::move(ptr->waited.value());
}
}  // namespace taihe

#include <type_traits>

namespace taihe {
template<typename...>
constexpr inline bool dependent_false_v = false;

template<typename Next, typename Last, typename Processor>
future<Next> then(future<Last> old, Processor &&processor)
{
    auto [com, fut] = make_async_pair<Next>();

    struct ProcessHandler {
        Processor processor;
        completer<Next> com;

        ProcessHandler(Processor &&processor, completer<Next> com)
            : processor(std::forward<Processor>(processor)), com(std::move(com))
        {
        }

        struct CompleterAsHandler {
            completer<Next> com;

            explicit CompleterAsHandler(completer<Next> com) : com(std::move(com))
            {
            }

            void operator()(Next &&result) const
            {
                com.complete(std::forward<Next>(result));
            }
        };

        void operator()(Last &&result)
        {
            if constexpr (std::is_invocable_r_v<future<Next>, Processor, Last>) {
                this->processor(std::forward<Last>(result))
                    .template on_complete<CompleterAsHandler>(std::move(this->com));
            } else if constexpr (std::is_invocable_v<Processor, Last, completer<Next>>) {
                this->processor(std::forward<Last>(result), std::move(this->com));
            } else {
                static_assert(dependent_false_v<Next, Last, Processor>,
                              "Processor cannot handle result without completer or future return type");
            }
        }
    };

    old.template on_complete<ProcessHandler>(std::forward<Processor>(processor), std::move(com));
    return std::move(fut);
}
}  // namespace taihe

#endif  // TAIHE_ASYNC_HPP
