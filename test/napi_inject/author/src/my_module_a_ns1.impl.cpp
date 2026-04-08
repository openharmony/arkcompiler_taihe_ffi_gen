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

#include <cstdint>
#include <iostream>
#include "my_module_a.ns1.impl.hpp"
#include "my_module_a.ns1.proj.hpp"

namespace {
::taihe::expected<::taihe::string, ::taihe::error> Funtest(::my_module_a::ns1::Color s)
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

::taihe::expected<void, ::taihe::error> noo()
{
    std::cout << "namespace: my_module_a.ns1, func: noo" << std::endl;
    return {};
}

class Base {
protected:
    ::taihe::string id;
    ::taihe::string name = "default_name";

public:
    Base(::taihe::string_view id) : id(id)
    {
        std::cout << "new base " << this << std::endl;
    }

    ~Base()
    {
        std::cout << "del base " << this << std::endl;
    }

    ::taihe::expected<::taihe::string, ::taihe::error> getName()
    {
        return name;
    }

    ::taihe::expected<void, ::taihe::error> setName(::taihe::string_view s)
    {
        name = s;
        return {};
    }

    ::taihe::expected<::taihe::string, ::taihe::error> getId()
    {
        return id;
    }

    ::taihe::expected<void, ::taihe::error> setId(::taihe::string_view s)
    {
        id = s;
        return {};
    }
};

::taihe::expected<::my_module_a::ns1::IBase, ::taihe::error> makeIBase(::taihe::string_view id)
{
    return taihe::make_holder<Base, ::my_module_a::ns1::IBase>(id);
}

::taihe::expected<void, ::taihe::error> bar()
{
    std::cout << "namespace: my_module_b.functiontest, func: bar" << std::endl;
    return {};
}

class CTestImpl {
    int32_t x;
    ::taihe::string id = "default_id";
    ::taihe::string name = "default_name";

public:
    CTestImpl(int32_t x) : x(x)
    {
        std::cout << "new ctest " << this->x << std::endl;
    }

    ~CTestImpl()
    {
        std::cout << "del ctest " << this << std::endl;
    }

    ::taihe::expected<::taihe::string, ::taihe::error> getName()
    {
        return name;
    }

    ::taihe::expected<void, ::taihe::error> setName(::taihe::string_view s)
    {
        name = s;
        return {};
    }

    ::taihe::expected<float, ::taihe::error> add(int32_t a, int32_t b)
    {
        return a + b + this->x;
    }
};

::taihe::expected<::my_module_a::ns1::CTest, ::taihe::error> createCTest(int32_t id)
{
    return taihe::make_holder<CTestImpl, ::my_module_a::ns1::CTest>(id);
}

::taihe::expected<::my_module_a::ns1::CTest, ::taihe::error> changeCTest(::my_module_a::ns1::weak::CTest a)
{
    constexpr int OPERAND_A = 3;
    constexpr int OPERAND_B = 4;
    ::taihe::expected<int32_t, ::taihe::error> x = a->add(OPERAND_A, OPERAND_B);
    if (x.has_value()) {
        return taihe::make_holder<CTestImpl, ::my_module_a::ns1::CTest>(x.value());
    } else {
        return ::taihe::expected<::my_module_a::ns1::CTest, ::taihe::error>(::taihe::unexpect, x.error());
    }
}

::taihe::expected<int32_t, ::taihe::error> multiply(int32_t a, int32_t b)
{
    return a * b;
}

class IfaceCImpl {
public:
    ::taihe::expected<void, ::taihe::error> func3()
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> func2()
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> func1()
    {
        return {};
    }
};

::taihe::expected<::my_module_a::ns1::C, ::taihe::error> createC()
{
    return ::my_module_a::ns1::C {{{1}, 2}, 3};
}

::taihe::expected<::my_module_a::ns1::IfaceC, ::taihe::error> createIfaceC()
{
    return taihe::make_holder<IfaceCImpl, ::my_module_a::ns1::IfaceC>();
}
}  // namespace

TH_EXPORT_CPP_API_Funtest(Funtest);
TH_EXPORT_CPP_API_noo(noo);
TH_EXPORT_CPP_API_makeIBase(makeIBase);
TH_EXPORT_CPP_API_bar(bar);
TH_EXPORT_CPP_API_createCTest(createCTest);
TH_EXPORT_CPP_API_changeCTest(changeCTest);
TH_EXPORT_CPP_API_multiply(multiply);
TH_EXPORT_CPP_API_createC(createC);
TH_EXPORT_CPP_API_createIfaceC(createIfaceC);
// NOLINTEND
