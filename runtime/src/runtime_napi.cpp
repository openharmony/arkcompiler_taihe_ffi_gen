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

#include <taihe/runtime.hpp>

namespace taihe {

namespace {
thread_local napi_env thread_env = nullptr;
}  // namespace

void set_env(napi_env env)
{
    thread_env = env;
}

napi_env get_env()
{
    return thread_env;
}

void set_error(taihe::string_view msg, ::taihe::string_view errcode)
{
    napi_env env = get_env();
    char const *code = !errcode.empty() ? errcode.c_str() : nullptr;
    napi_throw_error(env, code, msg.c_str());
}

void set_type_error(taihe::string_view msg, ::taihe::string_view errcode)
{
    napi_env env = get_env();
    char const *code = !errcode.empty() ? errcode.c_str() : nullptr;
    napi_throw_type_error(env, code, msg.c_str());
}

void set_range_error(taihe::string_view msg, ::taihe::string_view errcode)
{
    napi_env env = get_env();
    char const *code = !errcode.empty() ? errcode.c_str() : nullptr;
    napi_throw_range_error(env, code, msg.c_str());
}

bool has_error()
{
    napi_env env = get_env();
    bool has_error = false;
    napi_is_exception_pending(env, &has_error);
    return has_error;
}

::taihe::error from_napi_error(napi_value err)
{
    napi_env env = get_env();
    napi_value error_message_napi;
    NAPI_CALL(env, napi_get_named_property(env, err, "message", &error_message_napi));
    size_t error_message_cpp_len = 0;
    NAPI_CALL(env, napi_get_value_string_utf8(env, error_message_napi, nullptr, 0, &error_message_cpp_len));
    TString error_message_tstr;
    char *error_message_cpp_buf = tstr_initialize(&error_message_tstr, error_message_cpp_len + 1);
    NAPI_CALL(env, napi_get_value_string_utf8(env, error_message_napi, error_message_cpp_buf, error_message_cpp_len + 1,
                                              &error_message_cpp_len));
    error_message_cpp_buf[error_message_cpp_len] = '\0';
    error_message_tstr.length = error_message_cpp_len;
    taihe::string error_message_cpp(error_message_tstr);
    bool error_has_code;
    NAPI_CALL(env, napi_has_named_property(env, err, "code", &error_has_code));
    if (error_has_code) {
        napi_value error_code_napi;
        NAPI_CALL(env, napi_get_named_property(env, err, "code", &error_code_napi));
        napi_valuetype error_code_napi_type;
        NAPI_CALL(env, napi_typeof(env, error_code_napi, &error_code_napi_type));
        int32_t error_code_cpp = 0;
        switch (error_code_napi_type) {
            case napi_string: {
                size_t error_code_napi_len = 0;
                NAPI_CALL(env, napi_get_value_string_utf8(env, error_code_napi, nullptr, 0, &error_code_napi_len));
                char error_code_napi_buffer[error_code_napi_len + 1];
                size_t error_code_napi_copied;
                NAPI_CALL(env, napi_get_value_string_utf8(env, error_code_napi, error_code_napi_buffer,
                                                          error_code_napi_len + 1, &error_code_napi_copied));
                error_code_napi_buffer[error_code_napi_len] = '\0';
                error_code_cpp = std::stoi(error_code_napi_buffer);
                break;
            }
            case napi_number: {
                NAPI_CALL(env, napi_get_value_int32(env, error_code_napi, &error_code_cpp));
                break;
            }
            default: {
                return taihe::error(error_message_cpp);
            }
        }
        return taihe::error(error_message_cpp, error_code_cpp);
    } else {
        return taihe::error(error_message_cpp);
    }
}

napi_value into_napi_error(::taihe::error err)
{
    napi_env env = get_env();
    napi_value errorMessage = nullptr;
    napi_create_string_utf8(env, err.message().c_str(), NAPI_AUTO_LENGTH, &errorMessage);
    napi_value error = nullptr;
    if (err.code() != 0) {
        std::string code_str = std::to_string(err.code());
        char const *code = code_str.c_str();
        napi_value errorCode = nullptr;
        napi_create_string_utf8(env, code, NAPI_AUTO_LENGTH, &errorCode);
        napi_create_error(env, errorCode, errorMessage, &error);
    } else {
        napi_create_error(env, nullptr, errorMessage, &error);
    }
    return error;
}
}  // namespace taihe