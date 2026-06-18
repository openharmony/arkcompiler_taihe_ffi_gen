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

#include "debug.impl.hpp"

#include "taihe/runtime.hpp"

namespace {
// You can add using namespace statements here if needed.

::taihe::expected<void, ::taihe::error> TestMayThrowCallback(
    ::taihe::callback_view<::taihe::expected<void, ::taihe::error>()> mayThrowCallback)
{
    mayThrowCallback();
    return {};
}

::taihe::expected<void, ::taihe::error> TestNoThrowCallback(::taihe::callback_view<void()> noThrowCallback)
{
    noThrowCallback();
    return {};
}

::taihe::expected<void, ::taihe::error> TestBadParam(::taihe::array_view<::debug::IntOrStr> badParam)
{
    return {};
}

::taihe::expected<void, ::taihe::error> TestCallbackWithBadReturnType(
    ::taihe::callback_view<::taihe::expected<::debug::IntOrStr, ::taihe::error>()> callbackWithBadReturnType)
{
    callbackWithBadReturnType();
    return {};
}

::taihe::expected<::debug::MyEnum, ::taihe::error> TestReturnBadEnum()
{
    return ::debug::MyEnum(static_cast<::debug::MyEnum::key_t>(-1));
}

::taihe::expected<void, ::taihe::error> TestBadEnvGuard()
{
    class Guard {
    public:
        Guard()
        {
            old = taihe::get_vm();
        }

        ~Guard()
        {
            taihe::set_vm(old);
        }

    private:
        ani_vm *old;
    } temp;

    taihe::set_vm(nullptr);
    taihe::env_guard guard;
    return {};
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_TestMayThrowCallback(TestMayThrowCallback);
TH_EXPORT_CPP_API_TestNoThrowCallback(TestNoThrowCallback);
TH_EXPORT_CPP_API_TestBadParam(TestBadParam);
TH_EXPORT_CPP_API_TestCallbackWithBadReturnType(TestCallbackWithBadReturnType);
TH_EXPORT_CPP_API_TestReturnBadEnum(TestReturnBadEnum);
TH_EXPORT_CPP_API_TestBadEnvGuard(TestBadEnvGuard);
// NOLINTEND
