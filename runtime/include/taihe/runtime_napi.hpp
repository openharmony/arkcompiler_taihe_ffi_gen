/*
 * Copyright (c) 2025-2026 Huawei Device Co., Ltd.
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

#ifndef TAIHE_RUNTIME_NAPI_HPP
#define TAIHE_RUNTIME_NAPI_HPP

#if __has_include(<napi/native_api.h>)
#include <napi/native_api.h>
#elif __has_include(<node/node_api.h>)
#include <node/node_api.h>
#else
#error "Please ensure the napi is correctly installed."
#endif

#include <taihe/string.hpp>
#include <taihe/error.hpp>
#include <taihe/expected.hpp>

namespace taihe {
void set_env(napi_env env);
napi_env get_env();
}  // namespace taihe

#define TH_NAPI_ASSERT(cond, msg, ...)                                      \
    do {                                                                    \
        if (!(cond)) {                                                      \
            fprintf(stderr, "N-API Assertion failed: " msg, ##__VA_ARGS__); \
            std::abort();                                                   \
        }                                                                   \
    } while (0)

#define TH_NAPI_ASSUME_CALL(env, call)                                                               \
    do {                                                                                             \
        napi_status __status = (call);                                                               \
        TH_NAPI_ASSERT(__status == napi_ok, "N-API call " #call " failed with status %d", __status); \
    } while (0)

#define TH_NAPI_TRY_CALL(env, call)                                         \
    do {                                                                    \
        napi_status __status = (call);                                      \
        if (__status == napi_pending_exception) {                           \
            return ::taihe::unexpected(::taihe::catch_napi_exception(env)); \
        }                                                                   \
        if (__status != napi_ok) {                                          \
            return ::taihe::unexpected(::taihe::catch_napi_error(env));     \
        }                                                                   \
    } while (0)

#define TH_NAPI_ASSUME(expr)                                                                     \
    ({                                                                                           \
        auto &&__result = (expr);                                                                \
        TH_NAPI_ASSERT(__result.has_value(), "In expression " #expr ", status: %d, message: %s", \
                       __result.error().code(), __result.error().message().c_str());             \
        *::std::forward<decltype(__result)>(__result);                                           \
    })

#define TH_TRY_INTO_NAPI(env, expr)                               \
    ({                                                            \
        auto &&__result = (expr);                                 \
        if (!__result.has_value()) {                              \
            ::taihe::throw_napi_exception(env, __result.error()); \
            return nullptr;                                       \
        }                                                         \
        *::std::forward<decltype(__result)>(__result);            \
    })

namespace taihe {
taihe::expected<taihe::string, taihe::error> from_napi_string(napi_env env, napi_value str);
taihe::expected<taihe::u16string, taihe::error> from_napi_u16string(napi_env env, napi_value str);
taihe::expected<taihe::common_string, taihe::error> from_napi_common_string(napi_env env, napi_value str);
napi_value into_napi_string(napi_env env, taihe::string_view str);
napi_value into_napi_u16string(napi_env env, taihe::u16string_view str);
napi_value into_napi_common_string(napi_env env, taihe::common_string_view str);

taihe::error from_napi_exception(napi_env env, napi_value err);
napi_value into_napi_exception(napi_env env, taihe::error const &err);

void throw_napi_exception(napi_env env, taihe::error const &err);
taihe::error catch_napi_exception(napi_env env);
taihe::error catch_napi_error(napi_env env);
}  // namespace taihe

#endif  // TAIHE_RUNTIME_NAPI_HPP
