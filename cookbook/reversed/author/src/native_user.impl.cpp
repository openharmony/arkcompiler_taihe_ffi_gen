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

// This file is a test file.
// NOLINTBEGIN
#include "native_user.impl.hpp"
#include <iostream>
#include "native_user.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

namespace {
// To be implemented.

::taihe::expected<::taihe::string, ::taihe::error> UseIfaceA(::impl::weak::IfaceA_taihe obj)
{
    auto foo_res = obj->Foo();
    auto bar_res = obj->Bar();
    if (foo_res.has_value()) {
        std::cout << "native call Foo(): " << foo_res.value() << std::endl;
    }
    if (bar_res.has_value()) {
        std::cout << "native call Bar(): " << bar_res.value() << std::endl;
    }
    if (foo_res.has_value()) {
        return foo_res.value();
    }
    return ::taihe::unexpected<::taihe::error>(::taihe::error {"No value in Foo"});
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
TH_EXPORT_CPP_API_UseIfaceA(UseIfaceA);
// NOLINTEND
