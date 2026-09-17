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

#include <taihe/runtime_napi.hpp>

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
}  // namespace taihe

namespace taihe {
taihe::expected<taihe::string, taihe::error> from_napi_string(napi_env env, napi_value str)
{
    size_t strLength = 0;
    TH_NAPI_TRY_CALL(env, napi_get_value_string_utf8(env, str, nullptr, 0, &strLength));
    taihe::string_builder strBuilder(strLength + 1);
    TH_NAPI_TRY_CALL(env, napi_get_value_string_utf8(env, str, strBuilder.data(), strBuilder.capacity(), &strLength));
    return std::move(strBuilder).finish(strLength);
}

taihe::expected<taihe::u16string, taihe::error> from_napi_u16string(napi_env env, napi_value str)
{
    size_t strLength = 0;
    TH_NAPI_TRY_CALL(env, napi_get_value_string_utf16(env, str, nullptr, 0, &strLength));
    taihe::u16string_builder strBuilder(strLength + 1);
    TH_NAPI_TRY_CALL(env, napi_get_value_string_utf16(env, str, strBuilder.data(), strBuilder.capacity(), &strLength));
    return std::move(strBuilder).finish(strLength);
}

taihe::expected<taihe::common_string, taihe::error> from_napi_common_string(napi_env env, napi_value str)
{
    return from_napi_u16string(env, str);
}

napi_value into_napi_string(napi_env env, taihe::string_view str)
{
    napi_value napiStr = nullptr;
    TH_NAPI_ASSUME_CALL(env, napi_create_string_utf8(env, str.data(), str.size(), &napiStr));
    return napiStr;
}

napi_value into_napi_u16string(napi_env env, taihe::u16string_view str)
{
    napi_value napiStr = nullptr;
    TH_NAPI_ASSUME_CALL(env, napi_create_string_utf16(env, str.data(), str.size(), &napiStr));
    return napiStr;
}

napi_value into_napi_common_string(napi_env env, taihe::common_string_view str)
{
    if (str.is_utf8()) {
        return into_napi_string(env, taihe::string_view(str));
    }
    if (str.is_utf16()) {
        return into_napi_u16string(env, taihe::u16string_view(str));
    }
    napi_value undefined;
    TH_NAPI_ASSUME_CALL(env, napi_get_undefined(env, &undefined));
    return undefined;
}

taihe::error from_napi_exception(napi_env env, napi_value err)
{
    napi_value error_message_napi;
    TH_NAPI_ASSUME_CALL(env, napi_get_named_property(env, err, "message", &error_message_napi));
    auto error_message_cpp = from_napi_common_string(env, error_message_napi);
    if (!error_message_cpp) {
        return std::move(error_message_cpp.error());
    }
    bool error_has_code;
    TH_NAPI_ASSUME_CALL(env, napi_has_named_property(env, err, "code", &error_has_code));
    if (error_has_code) {
        napi_value error_code_napi;
        TH_NAPI_ASSUME_CALL(env, napi_get_named_property(env, err, "code", &error_code_napi));
        napi_valuetype error_code_napi_type;
        TH_NAPI_ASSUME_CALL(env, napi_typeof(env, error_code_napi, &error_code_napi_type));
        int32_t error_code_cpp = 0;
        switch (error_code_napi_type) {
            case napi_string: {
                size_t error_code_napi_len = 0;
                TH_NAPI_ASSUME_CALL(env,
                                    napi_get_value_string_utf8(env, error_code_napi, nullptr, 0, &error_code_napi_len));
                std::string error_code_napi_buffer(error_code_napi_len + 1, '\0');
                TH_NAPI_ASSUME_CALL(env,
                                    napi_get_value_string_utf8(env, error_code_napi, error_code_napi_buffer.data(),
                                                               error_code_napi_buffer.size(), &error_code_napi_len));
                error_code_cpp = std::stoi(error_code_napi_buffer);
                break;
            }
            case napi_number: {
                TH_NAPI_ASSUME_CALL(env, napi_get_value_int32(env, error_code_napi, &error_code_cpp));
                break;
            }
            default: {
                return taihe::error(std::move(error_message_cpp.value()));
            }
        }
        return taihe::error(std::move(error_message_cpp.value()), error_code_cpp);
    } else {
        return taihe::error(std::move(error_message_cpp.value()));
    }
}

napi_value into_napi_exception(napi_env env, taihe::error const &err)
{
    napi_value errorMessage = into_napi_common_string(env, err.common_message());
    napi_value errorCode = nullptr;
    if (err.code() != 0) {
        std::string errorCodeStr = std::to_string(err.code());
        TH_NAPI_ASSUME_CALL(env, napi_create_string_utf8(env, errorCodeStr.c_str(), NAPI_AUTO_LENGTH, &errorCode));
    }
    napi_value error = nullptr;
    TH_NAPI_ASSUME_CALL(env, napi_create_error(env, errorCode, errorMessage, &error));
    return error;
}

void throw_napi_exception(napi_env env, taihe::error const &err)
{
    napi_value error = into_napi_exception(env, err);
    TH_NAPI_ASSUME_CALL(env, napi_throw(env, error));
}

taihe::error catch_napi_exception(napi_env env)
{
    napi_value error;
    TH_NAPI_ASSUME_CALL(env, napi_get_and_clear_last_exception(env, &error));
    return from_napi_exception(env, error);
}

taihe::error catch_napi_error(napi_env env)
{
    napi_extended_error_info const *info;
    TH_NAPI_ASSUME_CALL(env, napi_get_last_error_info(env, &info));
    char const *message = info ? info->error_message : "<unknown>";
    return ::taihe::error(message);
}
}  // namespace taihe