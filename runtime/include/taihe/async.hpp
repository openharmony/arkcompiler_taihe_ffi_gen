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
    void (*process_handler_ptr)(TAsyncHandlerStorage storage, Result *result_ptr);
    void (*cleanup_handler_ptr)(TAsyncHandlerStorage storage);

    ResultBuffer buffer;

    async_context(async_context const &) = delete;
    async_context &operator=(async_context const &) = delete;
    async_context(async_context &&) = delete;
    async_context &operator=(async_context &&) = delete;

    async_context(uint32_t ref_count)
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
        process_handler_ptr(storage, &buffer.result);
    }

    void cleanup_handler()
    {
        cleanup_handler_ptr(storage);
    }

    template<typename... Args>
    void emplace_result(Args &&...args)
    {
        TH_ASSERT(!(flags & ASYNC_CONTEXT_RESULT_SET), "Result is already being set");
        new (&buffer.result) Result(std::forward<Args>(args)...);

        uint32_t old_falgs = set_flags(ASYNC_CONTEXT_RESULT_SET);
        if (old_falgs & ASYNC_CONTEXT_HANDLER_SET) {
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
        process_handler_ptr = [](TAsyncHandlerStorage storage, Result *result_ptr) {
            reinterpret_cast<SmallConstHandler const *>(&storage.buf)->handle_result(std::forward<Result>(*result_ptr));
        };
        cleanup_handler_ptr = [](TAsyncHandlerStorage storage) {
            reinterpret_cast<SmallConstHandler const *>(&storage.buf)->~SmallConstHandler();
        };

        uint32_t old_falgs = set_flags(ASYNC_CONTEXT_HANDLER_SET);
        if (old_falgs & ASYNC_CONTEXT_RESULT_SET) {
            process_handler();
        }
    }

    template<typename LargeMutableHandler, typename... Args>
    void new_handler(Args &&...args)
    {
        TH_ASSERT(!(flags & ASYNC_CONTEXT_HANDLER_SET), "Handler is already being set");
        storage.ptr = new LargeMutableHandler(std::forward<Args>(args)...);
        process_handler_ptr = [](TAsyncHandlerStorage storage, Result *result_ptr) {
            reinterpret_cast<LargeMutableHandler *>(storage.ptr)->handle_result(std::forward<Result>(*result_ptr));
        };
        cleanup_handler_ptr = [](TAsyncHandlerStorage storage) {
            delete reinterpret_cast<LargeMutableHandler *>(storage.ptr);
        };

        uint32_t old_falgs = set_flags(ASYNC_CONTEXT_HANDLER_SET);
        if (old_falgs & ASYNC_CONTEXT_RESULT_SET) {
            process_handler();
        }
    }

    bool is_ready() const
    {
        return flags & ASYNC_CONTEXT_RESULT_SET;
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
class async_completer;

template<typename Result>
class async_future;

template<typename Result>
std::pair<async_completer<Result>, async_future<Result>> make_async_pair();

template<typename Result>
class async_completer {
public:
    async_context<Result> *m_ctx;

    async_completer(async_context<Result> *ctx) : m_ctx(ctx)
    {
    }

    friend std::pair<async_completer<Result>, async_future<Result>> make_async_pair<Result>();

    async_completer(async_completer const &) = delete;

    async_completer(async_completer &&other) : m_ctx(other.m_ctx)
    {
        other.m_ctx = nullptr;
    }

    async_completer &operator=(async_completer other)
    {
        std::swap(this->m_ctx, other.m_ctx);
        return *this;
    }

    ~async_completer()
    {
        if (m_ctx && m_ctx->dec_ref()) {
            delete m_ctx;
        }
    }

    template<typename... Args>
    void emplace_result(Args &&...args) const
    {
        m_ctx->emplace_result(std::forward<Args>(args)...);
    }
};

template<typename Result>
class async_future {
public:
    async_context<Result> *m_ctx;

    async_future(async_context<Result> *ctx) : m_ctx(ctx)
    {
    }

    friend std::pair<async_completer<Result>, async_future<Result>> make_async_pair<Result>();

    async_future(async_future const &) = delete;

    async_future(async_future &&other) : m_ctx(other.m_ctx)
    {
        other.m_ctx = nullptr;
    }

    async_future &operator=(async_future other)
    {
        std::swap(this->m_ctx, other.m_ctx);
        return *this;
    }

    ~async_future()
    {
        if (m_ctx && m_ctx->dec_ref()) {
            delete m_ctx;
        }
    }

    template<typename SmallConstHandler, typename... Args>
    void emplace_handler(Args &&...args) const
    {
        m_ctx->template emplace_handler<SmallConstHandler>(std::forward<Args>(args)...);
    }

    template<typename LargeMutableHandler, typename... Args>
    void new_handler(Args &&...args) const
    {
        m_ctx->template new_handler<LargeMutableHandler>(std::forward<Args>(args)...);
    }

    bool is_ready() const
    {
        return m_ctx->is_ready();
    }
};

template<typename Result>
std::pair<async_completer<Result>, async_future<Result>> make_async_pair()
{
    async_context<Result> *ctx = new async_context<Result>(2);
    return {
        async_completer<Result>(ctx),
        async_future<Result>(ctx),
    };
}

template<typename Result>
struct as_abi<async_completer<Result>> {
    using type = TAsyncCompleter;
};

template<typename Result>
struct as_abi<async_future<Result>> {
    using type = TAsyncFuture;
};

template<typename Result>
struct as_param<async_completer<Result>> {
    using type = async_completer<Result>;
};

template<typename Result>
struct as_param<async_future<Result>> {
    using type = async_future<Result>;
};

template<typename Result>
inline bool operator==(async_completer<Result> lhs, async_completer<Result> rhs)
{
    return lhs.m_ctx == rhs.m_ctx;
}

template<typename Result>
inline bool operator==(async_future<Result> lhs, async_future<Result> rhs)
{
    return lhs.m_ctx == rhs.m_ctx;
}
}  // namespace taihe

template<typename Result>
struct std::hash<taihe::async_completer<Result>> {
    std::size_t operator()(taihe::async_completer<Result> val) const
    {
        return std::hash<void *>()(val.m_ctx);
    }
};

template<typename Result>
struct std::hash<taihe::async_future<Result>> {
    std::size_t operator()(taihe::async_future<Result> val) const
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
Result join(async_future<Result> future)
{
    struct JoinContext {
        std::mutex mtx;
        std::condition_variable cv;
        std::optional<Result> joined;
    };

    struct JoinHandler {
        JoinContext &ctx;

        JoinHandler(JoinContext &ctx) : ctx(ctx)
        {
        }

        void handle_result(Result &&result) const
        {
            std::unique_lock<std::mutex> lock(ctx.mtx);
            ctx.joined.emplace(std::forward<Result>(result));
            ctx.cv.notify_all();
        }
    };

    JoinContext ctx;
    future.template emplace_handler<JoinHandler>(ctx);

    std::unique_lock<std::mutex> lock(ctx.mtx);
    ctx.cv.wait(lock, [&ctx]() {
        return ctx.joined.has_value();
    });

    return std::move(ctx.joined.value());
}

template<typename Result>
Result select(std::initializer_list<async_future<Result>> futures)
{
    struct SelectContext {
        std::mutex mtx;
        std::condition_variable cv;
        std::optional<Result> joined;
    };

    struct SelectHandler {
        std::shared_ptr<SelectContext> ptr;

        SelectHandler(std::shared_ptr<SelectContext> ptr) : ptr(ptr)
        {
        }

        void handle_result(Result &&result) const
        {
            std::unique_lock<std::mutex> lock(ptr->mtx);
            if (!ptr->joined.has_value()) {
                ptr->joined.emplace(std::forward<Result>(result));
                ptr->cv.notify_all();
            }
        }
    };

    auto ptr = std::make_shared<SelectContext>();
    for (auto const &old : futures) {
        old.template emplace_handler<SelectHandler>(ptr);
    }

    std::unique_lock<std::mutex> lock(ptr->mtx);
    ptr->cv.wait(lock, [ptr = ptr.get()]() {
        return ptr->joined.has_value();
    });

    return std::move(ptr->joined.value());
}
}  // namespace taihe

#include <type_traits>

namespace taihe {
template<typename...>
constexpr inline bool dependent_false_v = false;

template<typename Next, typename Last, typename Processor>
async_future<Next> then(async_future<Last> prev, Processor &&processor)
{
    auto [completer, future] = make_async_pair<Next>();

    struct ProcessHandler {
        Processor processor;
        async_completer<Next> completer;

        ProcessHandler(Processor &&processor, async_completer<Next> completer)
            : processor(std::forward<Processor>(processor)), completer(std::move(completer))
        {
        }

        struct CompleterAsHandler {
            async_completer<Next> completer;

            CompleterAsHandler(async_completer<Next> completer) : completer(std::move(completer))
            {
            }

            void handle_result(Next &&result) const
            {
                completer.emplace_result(std::forward<Next>(result));
            }
        };

        void handle_result(Last &&result)
        {
            if constexpr (std::is_invocable_r_v<async_future<Next>, Processor, Last>) {
                this->processor(std::forward<Last>(result))
                    .template emplace_handler<CompleterAsHandler>(std::move(this->completer));
            } else if constexpr (std::is_invocable_v<Processor, Last, async_completer<Next>>) {
                this->processor(std::forward<Last>(result), std::move(this->completer));
            } else {
                static_assert(dependent_false_v<Next, Last, Processor>,
                              "Processor cannot handle result without completer or future return type");
            }
        }
    };

    prev.template new_handler<ProcessHandler>(std::forward<Processor>(processor), std::move(completer));
    return std::move(future);
}
}  // namespace taihe

#endif  // TAIHE_ASYNC_HPP
