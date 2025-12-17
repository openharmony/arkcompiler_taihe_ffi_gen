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
napi_env global_env = nullptr;
thread_local napi_env thread_env = nullptr;
}  // namespace

void set_env(napi_env env)
{
    global_env = env;
}

napi_env get_env()
{
    return thread_env ? thread_env : global_env;
}

EnvGuard::EnvGuard(napi_env env) : env_(env)
{
    if (!env_) {
        env_ = global_env;
    }
    thread_env = env_;
}

EnvGuard::~EnvGuard()
{
    thread_env = nullptr;
}

void set_error(taihe::string_view msg, ::taihe::string_view errcode)
{
    EnvGuard guard;
    napi_env env = guard.env();

    char const *code = !errcode.empty() ? errcode.c_str() : nullptr;
    napi_throw_error(env, code, msg.c_str());
}

void set_type_error(taihe::string_view msg, ::taihe::string_view errcode)
{
    EnvGuard guard;
    napi_env env = guard.env();

    char const *code = !errcode.empty() ? errcode.c_str() : nullptr;
    napi_throw_type_error(env, code, msg.c_str());
}

void set_range_error(taihe::string_view msg, ::taihe::string_view errcode)
{
    EnvGuard guard;
    napi_env env = guard.env();

    char const *code = !errcode.empty() ? errcode.c_str() : nullptr;
    napi_throw_range_error(env, code, msg.c_str());
}

bool has_error()
{
    EnvGuard guard;
    napi_env env = guard.env();
    bool has_error = false;
    napi_is_exception_pending(env, &has_error);
    return has_error;
}
}  // namespace taihe