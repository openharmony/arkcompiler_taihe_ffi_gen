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

#ifndef TAIHE_PLATFORM_NAPI_HPP
#define TAIHE_PLATFORM_NAPI_HPP

#include <atomic>
#include <condition_variable>
#include <functional>
#include <mutex>
#include <optional>
#include <pthread.h>
#include <tuple>
#include <type_traits>
#include <utility>

#include <taihe/array.hpp>
#include <taihe/object.hpp>
#include <taihe/runtime_napi.hpp>

#include <taihe.platform.napi.proj.hpp>

namespace taihe {
class ThreadContext {
public:
    static ThreadContext &get_instance()
    {
        static ThreadContext instance;
        return instance;
    }

    void init_main_thread_id()
    {
        static std::once_flag flag;
        std::call_once(flag, [this]() {
            main_thread_id_ = pthread_self();
            initialized_ = true;
        });
    }

    bool is_main_thread() const
    {
        if (!initialized_) {
            return false;
        }
        return pthread_equal(pthread_self(), main_thread_id_) != 0;
    }

    ThreadContext(ThreadContext const &) = delete;
    ThreadContext &operator=(ThreadContext const &) = delete;

private:
    ThreadContext() = default;
    pthread_t main_thread_id_;
    bool initialized_ = false;
};

inline bool _is_main_thread()
{
    return ThreadContext::get_instance().is_main_thread();
}

inline void _init_main_thread()
{
    ThreadContext::get_instance().init_main_thread_id();
}

struct napi_ref_guard {
private:
    struct threadsafe_call {
        virtual void invoke(napi_env env) = 0;
        virtual ~threadsafe_call() = default;
    };

    napi_env env_;
    napi_ref ref_;
    napi_threadsafe_function tsfn_;

    static void dispatch_threadsafe_call(napi_env env, [[maybe_unused]] napi_value js_cb,
                                         [[maybe_unused]] void *context, void *data)
    {
        auto *call = static_cast<threadsafe_call *>(data);
        call->invoke(env);
    }

protected:
    template<typename callable_t, typename... arg_t>
    auto sync_call(callable_t &&callable, arg_t &&...args)
        -> std::invoke_result_t<std::decay_t<callable_t> &, napi_env, napi_ref, std::decay_t<arg_t> &...>
    {
        using result_t = std::invoke_result_t<std::decay_t<callable_t> &, napi_env, napi_ref, std::decay_t<arg_t> &...>;

        struct no_result_t {};

        using stored_result_t = std::conditional_t<std::is_void_v<result_t>, no_result_t, result_t>;

        if (::taihe::_is_main_thread()) {
            return std::invoke(std::forward<callable_t>(callable), env_, ref_, std::forward<arg_t>(args)...);
        }

        struct sync_call_data final : threadsafe_call {
            std::mutex mutex;
            std::condition_variable cv;
            napi_ref ref;
            std::decay_t<callable_t> callable;
            std::tuple<std::decay_t<arg_t>...> args;
            std::optional<stored_result_t> result;

            sync_call_data(napi_ref ref, callable_t &&callable, arg_t &&...args)
                : ref(ref), callable(std::forward<callable_t>(callable)), args(std::forward<arg_t>(args)...)
            {
            }

            void invoke(napi_env env) override
            {
                std::lock_guard<std::mutex> lock(this->mutex);
                if constexpr (std::is_void_v<result_t>) {
                    std::apply(
                        [this, env](auto &...args) {
                            std::invoke(this->callable, env, this->ref, args...);
                        },
                        this->args);
                    this->result.emplace();
                } else {
                    this->result = std::apply(
                        [this, env](auto &...args) {
                            return std::invoke(this->callable, env, this->ref, args...);
                        },
                        this->args);
                }
                this->cv.notify_one();
            }
        };

        sync_call_data call_data(ref_, std::forward<callable_t>(callable), std::forward<arg_t>(args)...);
        NAPI_CALL(env_,
                  napi_call_threadsafe_function(tsfn_, static_cast<threadsafe_call *>(&call_data), napi_tsfn_blocking));
        std::unique_lock<std::mutex> lock(call_data.mutex);
        call_data.cv.wait(lock, [&call_data] {
            return call_data.result.has_value();
        });

        if constexpr (std::is_void_v<result_t>) {
            return;
        } else {
            return std::move(*call_data.result);
        }
    }

public:
    explicit napi_ref_guard(napi_env env) : env_(env), ref_(nullptr), tsfn_(nullptr)
    {
    }

    napi_ref_guard(napi_env env, napi_value callback) : napi_ref_guard(env)
    {
        NAPI_CALL(env, napi_create_reference(env, callback, 1, &ref_));
        napi_value napi_resname;
        NAPI_CALL(env, napi_create_string_utf8(env, "MyWorkResource", NAPI_AUTO_LENGTH, &napi_resname));
        NAPI_CALL(env, napi_create_threadsafe_function(env, nullptr, nullptr, napi_resname, 0, 1, nullptr, nullptr,
                                                       nullptr, napi_ref_guard::dispatch_threadsafe_call, &tsfn_));
        napi_unref_threadsafe_function(env, tsfn_);
    }

    ~napi_ref_guard()
    {
        if (ref_) {
            this->sync_call([](napi_env env, napi_ref ref) {
                NAPI_CALL(env, napi_delete_reference(env, ref));
            });
        }
        if (tsfn_) {
            NAPI_CALL(env_, napi_release_threadsafe_function(tsfn_, napi_tsfn_release));
        }
    }

    napi_ref_guard(napi_ref_guard const &) = delete;
    napi_ref_guard &operator=(napi_ref_guard const &) = delete;

    uintptr_t getGlobalReference() const
    {
        return reinterpret_cast<uintptr_t>(ref_);
    }
};

inline bool _get_bigint_msb(uint64_t dig)
{
    return dig >> (sizeof(uint64_t) * 8 - 1) != 0;
}

inline bool _get_bigint_sign(taihe::array_view<uint64_t> num)
{
    return _get_bigint_msb(num[num.size() - 1]);
}

inline std::pair<bool, taihe::array<uint64_t>> _get_bigint_sign_and_abs(taihe::array_view<uint64_t> num)
{
    uint64_t *buf = reinterpret_cast<uint64_t *>(malloc(num.size() * sizeof(uint64_t)));
    bool sign = _get_bigint_msb(num[num.size() - 1]);
    if (sign) {
        bool carry = true;
        for (std::size_t i = 0; i < num.size(); i++) {
            buf[i] = ~num[i] + carry;
            carry = carry && (buf[i] == 0);
        }
    } else {
        for (std::size_t i = 0; i < num.size(); i++) {
            buf[i] = num[i];
        }
    }
    std::size_t size = num.size();
    while (size > 0 && buf[size - 1] == 0) {
        size--;
    }
    return {sign, taihe::array<uint64_t>(buf, size)};
}

inline taihe::array<uint64_t> _build_num(bool sign, taihe::array_view<uint64_t> abs)
{
    uint64_t *buf = reinterpret_cast<uint64_t *>(malloc((abs.size() + 1) * sizeof(uint64_t)));
    if (sign) {
        bool carry = true;
        for (std::size_t i = 0; i < abs.size(); i++) {
            buf[i] = ~abs[i] + carry;
            carry = carry && (buf[i] == 0);
        }
        buf[abs.size()] = carry - 1;
    } else {
        for (std::size_t i = 0; i < abs.size(); i++) {
            buf[i] = abs[i];
        }
        buf[abs.size()] = 0;
    }
    std::size_t size = abs.size() + 1;
    while (size >= 2 && ((buf[size - 1] == 0 && _get_bigint_msb(buf[size - 2]) == 0) ||
                         (buf[size - 1] == static_cast<uint64_t>(-1) && _get_bigint_msb(buf[size - 2]) == 1))) {
        size--;
    }
    return taihe::array<uint64_t>(buf, size);
}
}  // namespace taihe

#endif  // TAIHE_PLATFORM_NAPI_HPP
