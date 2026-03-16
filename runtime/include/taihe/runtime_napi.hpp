/*
 * Copyright (c) 2025 Huawei Device Co., Ltd.
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

#include <sstream>
#include <taihe/string.hpp>

namespace taihe {
void set_env(napi_env env);
napi_env get_env();

void set_error(::taihe::string_view msg, ::taihe::string_view errcode = "");
void set_type_error(::taihe::string_view msg, ::taihe::string_view errcode = "");
void set_range_error(::taihe::string_view msg, ::taihe::string_view errcode = "");
bool has_error();

class EnvGuard {
public:
    explicit EnvGuard(napi_env env = nullptr);
    ~EnvGuard();

    EnvGuard(EnvGuard const &) = delete;
    EnvGuard &operator=(EnvGuard const &) = delete;

    napi_env env() const
    {
        return env_;
    }

private:
    napi_env env_;
};

}  // namespace taihe

#define NAPI_CALL(env, call)                                                                \
    do {                                                                                    \
        napi_status status = (call);                                                        \
        if (status != napi_ok) {                                                            \
            const napi_extended_error_info *error_info;                                     \
            napi_get_last_error_info(env, &error_info);                                     \
            const char *message = error_info ? error_info->error_message : "Unknown error"; \
            std::ostringstream oss;                                                         \
            oss << "N-API call failed at " << __FILE__ << ":" << __LINE__ << "\n"           \
                << "Call: " << #call << "\n"                                                \
                << "Status: " << status << "\n"                                             \
                << "Message: " << message;                                                  \
            napi_throw_error(env, nullptr, oss.str().c_str());                              \
        }                                                                                   \
    } while (0)

namespace taihe {
// convert between napi types and taihe types

template<typename cpp_owner_t>
struct from_napi_t;

template<typename cpp_owner_t>
struct into_napi_t;

template<typename cpp_owner_t>
constexpr inline from_napi_t<cpp_owner_t> from_napi;

template<typename cpp_owner_t>
constexpr inline into_napi_t<cpp_owner_t> into_napi;
}  // namespace taihe

#endif  // TAIHE_RUNTIME_NAPI_HPP
