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
#include "callback.impl.hpp"

#include "callback.Person.proj.1.hpp"
#include "stdexcept"
#include "taihe/callback.hpp"
#include "taihe/string.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {

::taihe::expected<void, ::taihe::error> cb_void_void(
    ::taihe::callback_view<::taihe::expected<void, ::taihe::error>()> f)
{
    f();
    return {};
}

::taihe::expected<void, ::taihe::error> cb_i_void(
    ::taihe::callback_view<::taihe::expected<void, ::taihe::error>(int32_t)> f)
{
    f(1);
    return {};
}

::taihe::expected<::taihe::string, ::taihe::error> cb_str_str(
    ::taihe::callback_view<::taihe::expected<::taihe::string, ::taihe::error>(::taihe::string_view)> f)
{
    auto out = f("hello");
    return "hello";
}

::taihe::expected<void, ::taihe::error> cb_struct(
    ::taihe::callback_view<::taihe::expected<::callback::Person, ::taihe::error>(::callback::Person const &)> f)
{
    ::taihe::expected<::callback::Person, ::taihe::error> result = f(::callback::Person {"Tom", 18});
    std::cout << result.value().name << " " << result.value().age << std::endl;
    return {};
}
}  // namespace

TH_EXPORT_CPP_API_cb_void_void(cb_void_void);
TH_EXPORT_CPP_API_cb_i_void(cb_i_void);
TH_EXPORT_CPP_API_cb_str_str(cb_str_str);
TH_EXPORT_CPP_API_cb_struct(cb_struct);
// NOLINTEND
