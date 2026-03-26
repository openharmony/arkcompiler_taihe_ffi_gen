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
    napi_value exception;
    napi_get_and_clear_last_exception(env, &exception);
    if (exception == nullptr) {
        return false;
    }

    bool is_error = false;
    napi_is_error(env, exception, &is_error);
    return is_error;
}
}  // namespace taihe