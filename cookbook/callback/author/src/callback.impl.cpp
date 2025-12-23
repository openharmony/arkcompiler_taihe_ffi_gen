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

#include "callback.impl.hpp"

#include "callback.Person.proj.1.hpp"
#include "stdexcept"
#include "taihe/callback.hpp"
#include "taihe/string.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {
void cb_void_void(callback_view<void()> f)
{
    f();
}

void cb_i_void(callback_view<void(int32_t)> f)
{
    f(1);
}

string cb_str_str(callback_view<string(string_view)> f)
{
    taihe::string out = f("hello");
    return "hello";
}

void cb_struct(callback_view<::callback::Person(::callback::Person const &)> f)
{
    ::callback::Person result = f(::callback::Person {"Tom", 18});
    std::cout << result.name << " " << result.age << std::endl;
    return;
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_cb_void_void(cb_void_void);
TH_EXPORT_CPP_API_cb_i_void(cb_i_void);
TH_EXPORT_CPP_API_cb_str_str(cb_str_str);
TH_EXPORT_CPP_API_cb_struct(cb_struct);
// NOLINTEND
