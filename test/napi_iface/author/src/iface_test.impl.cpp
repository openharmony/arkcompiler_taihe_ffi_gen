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

#include "iface_test.impl.hpp"
#include <iostream>
#include "iface_test.proj.hpp"

namespace {

class Base {
protected:
    ::taihe::string id;

public:
    Base(::taihe::string_view id) : id(id)
    {
        std::cout << "new base " << this << std::endl;
    }

    ~Base()
    {
        std::cout << "del base " << this << std::endl;
    }

    ::taihe::string getId()
    {
        return id;
    }

    void setId(::taihe::string_view s)
    {
        id = s;
        return;
    }
};

class Shape {
protected:
    ::taihe::string id;
    float a;
    float b;

public:
    Shape(::taihe::string_view id, float a, float b) : id(id), a(a), b(b)
    {
        std::cout << "new shape " << this << std::endl;
    }

    ~Shape()
    {
        std::cout << "del shape " << this << std::endl;
    }

    ::taihe::string getId()
    {
        return id;
    }

    void setId(::taihe::string_view s)
    {
        id = s;
        return;
    }

    float calculateArea()
    {
        return a * b;
    }
};

class CTestImpl {
    int32_t x;

public:
    CTestImpl(int32_t x) : x(x)
    {
        std::cout << "new ctest " << this->x << std::endl;
    }

    ~CTestImpl()
    {
        std::cout << "del ctest " << this << std::endl;
    }

    float add(int32_t a, int32_t b)
    {
        return a + b + this->x;
    }
};

class Color {
protected:
    ::taihe::string id;

public:
    Color(::taihe::string_view id) : id(id)
    {
        std::cout << "new Color " << this << std::endl;
    }

    ~Color()
    {
        std::cout << "del Color " << this << std::endl;
    }

    ::taihe::string getId()
    {
        return id;
    }

    void setId(::taihe::string_view s)
    {
        id = s;
        return;
    }

    int32_t calculate(int32_t a, int32_t b)
    {
        return a * b;
    }
};

class Derived {
protected:
    ::taihe::string id = "d";
    float a = 1;
    float b = 2;

public:
    void call()
    {
        std::cout << "derived call!" << std::endl;
    }

    double calculateArea()
    {
        return a * b;
    }

    ::taihe::string getId()
    {
        return id;
    }

    void setId(::taihe::string_view s)
    {
        this->id = s;
        return;
    }
};

::iface_test::IBase makeIBase(::taihe::string_view id)
{
    return ::taihe::make_holder<Base, ::iface_test::IBase>(id);
}

void copyIBase(::iface_test::weak::IBase a, ::iface_test::weak::IBase b)
{
    a->setId(b->getId());
    return;
}

::iface_test::IShape makeIShape(::taihe::string_view id, double a, double b)
{
    return ::taihe::make_holder<Shape, ::iface_test::IShape>(id, a, b);
}

::iface_test::CTest createCTest(int32_t id)
{
    return taihe::make_holder<CTestImpl, ::iface_test::CTest>(id);
}

::iface_test::CTest changeCTest(::iface_test::weak::CTest a)
{
    int32_t x = a->add(3, 4);
    return taihe::make_holder<CTestImpl, ::iface_test::CTest>(x);
}

int32_t multiply(int32_t a, int32_t b)
{
    return a * b;
}

::iface_test::IColor makeIColor(::taihe::string_view id)
{
    // The parameters in the make_holder function should be of the same type
    // as the parameters in the constructor of the actual implementation class.
    return taihe::make_holder<Color, ::iface_test::IColor>(id);
}

void copyIColor(::iface_test::weak::IColor a, ::iface_test::weak::IColor b)
{
    a->setId(b->getId());
    return;
}

::iface_test::IDerived createIDerived()
{
    // The parameters in the make_holder function should be of the same type
    // as the parameters in the constructor of the actual implementation class.
    return taihe::make_holder<Derived, ::iface_test::IDerived>();
}
}  // namespace

TH_EXPORT_CPP_API_makeIBase(makeIBase);
TH_EXPORT_CPP_API_copyIBase(copyIBase);
TH_EXPORT_CPP_API_makeIShape(makeIShape);
TH_EXPORT_CPP_API_createCTest(createCTest);
TH_EXPORT_CPP_API_changeCTest(changeCTest);
TH_EXPORT_CPP_API_multiply(multiply);
TH_EXPORT_CPP_API_makeIColor(makeIColor);
TH_EXPORT_CPP_API_copyIColor(copyIColor);
TH_EXPORT_CPP_API_createIDerived(createIDerived);
// NOLINTEND
