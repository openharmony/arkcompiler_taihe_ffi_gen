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
#include "my_module_a.ns1.ns2.ns3.ns4.ns5.impl.hpp"
#include "my_module_a.ns1.ns2.ns3.ns4.ns5.proj.hpp"

namespace {

int32_t Funtest(::my_module_a::ns1::ns2::ns3::ns4::ns5::MyStruct const &s)
{
    return s.a + s.b;
}

void foo()
{
    std::cout << "namespace: my_module_a.ns1.ns2.ns3.ns4.ns5, func: noo" << std::endl;
}

::my_module_a::ns1::ns2::ns3::ns4::ns5::MyClass create_myclass(bool a, float b)
{
    return ::my_module_a::ns1::ns2::ns3::ns4::ns5::MyClass {a, b};
}

int32_t add(int32_t a, int32_t b)
{
    return a + b;
}

int32_t sum(int32_t a, int32_t b)
{
    return a * b;
}

::my_module_a::ns1::ns2::ns3::ns4::ns5::MyTest createMyTestNum(int32_t a)
{
    ::taihe::array<int32_t> temp {a};
    return {temp};
}

::my_module_a::ns1::ns2::ns3::ns4::ns5::MyTest createMyTestArrayNum(::taihe::array_view<int32_t> a)
{
    return {a};
}
}  // namespace

TH_EXPORT_CPP_API_Funtest(Funtest);
TH_EXPORT_CPP_API_foo(foo);
TH_EXPORT_CPP_API_create_myclass(create_myclass);
TH_EXPORT_CPP_API_add(add);
TH_EXPORT_CPP_API_sum(sum);
TH_EXPORT_CPP_API_createMyTestNum(createMyTestNum);
TH_EXPORT_CPP_API_createMyTestArrayNum(createMyTestArrayNum);
// NOLINTEND
