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

#include <iostream>
#include "my_module_a.ns1.impl.hpp"
#include "my_module_a.ns1.proj.hpp"

namespace {
::taihe::string Funtest(::my_module_a::ns1::Color s)
{
    switch (s.get_key()) {
        case ::my_module_a::ns1::Color::key_t::BLUE:
            return "blue";
        case ::my_module_a::ns1::Color::key_t::GREEN:
            return "green";
        case ::my_module_a::ns1::Color::key_t::RED:
            return "red";
    }
    return "error";
}

void noo()
{
    std::cout << "namespace: my_module_a.ns1, func: noo" << std::endl;
}
}  // namespace

TH_EXPORT_CPP_API_Funtest(Funtest);
TH_EXPORT_CPP_API_noo(noo);
// NOLINTEND
