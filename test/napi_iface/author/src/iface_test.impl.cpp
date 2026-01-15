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
    ::taihe::string name = "default_base_name";

public:
    Base(::taihe::string_view id) : id(id)
    {
        std::cout << "new base " << this << std::endl;
    }

    ~Base()
    {
        std::cout << "del base " << this << std::endl;
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

    ::taihe::expected<::taihe::string, ::taihe::error> getName()
    {
        return name;
    }

    ::taihe::expected<void, ::taihe::error> setName(::taihe::string_view s)
    {
        name = s;
        return {};
    }
};

class Shape {
protected:
    ::taihe::string id;
    float a;
    float b;
    ::taihe::string name = "default_shape_name";

public:
    Shape(::taihe::string_view id, float a, float b) : id(id), a(a), b(b)
    {
        std::cout << "new shape " << this << std::endl;
    }

    ~Shape()
    {
        std::cout << "del shape " << this << std::endl;
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

    ::taihe::expected<float, ::taihe::error> calculateArea()
    {
        return a * b;
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
};

class CTestImpl {
    int32_t x;
    ::taihe::string id = "default_ctest_id";

public:
    CTestImpl(int32_t x) : x(x)
    {
        std::cout << "new ctest " << this->x << std::endl;
    }

    ~CTestImpl()
    {
        std::cout << "del ctest " << this << std::endl;
    }

    ::taihe::expected<int32_t, ::taihe::error> add(int32_t a, int32_t b)
    {
        return a + b + this->x;
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

    ::taihe::expected<::taihe::string, ::taihe::error> getId()
    {
        return id;
    }

    ::taihe::expected<void, ::taihe::error> setId(::taihe::string_view s)
    {
        id = s;
        return {};
    }

    ::taihe::expected<int32_t, ::taihe::error> calculate(int32_t a, int32_t b)
    {
        return a * b;
    }
};

class Derived {
protected:
    ::taihe::string id = "d";
    float a = 1;
    float b = 2;
    ::taihe::string name = "default_derived_name";

public:
    ::taihe::expected<void, ::taihe::error> call()
    {
        std::cout << "derived call!" << std::endl;
        return {};
    }

    ::taihe::expected<double, ::taihe::error> calculateArea()
    {
        return a * b;
    }

    ::taihe::expected<::taihe::string, ::taihe::error> getId()
    {
        return id;
    }

    ::taihe::expected<void, ::taihe::error> setId(::taihe::string_view s)
    {
        this->id = s;
        return {};
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
};

::taihe::expected<::iface_test::IBase, ::taihe::error> makeIBase(::taihe::string_view id)
{
    return ::taihe::make_holder<Base, ::iface_test::IBase>(id);
}

::taihe::expected<void, ::taihe::error> copyIBase(::iface_test::weak::IBase a, ::iface_test::weak::IBase b)
{
    ::taihe::expected<::taihe::string, ::taihe::error> id = b->getId();
    if (id.has_value()) {
        auto x = a->setId(id.value());
        std::cout << x.has_value() << std::endl;
        return {};
    } else {
        std::cout << "!!!!!!!!!! Error in getting ID " << id.error().message().c_str() << id.error().code()
                  << std::endl;
        return ::taihe::expected<void, ::taihe::error>(::taihe::unexpect, "Error in getting ID");
    }
}

::taihe::expected<::iface_test::IShape, ::taihe::error> makeIShape(::taihe::string_view id, double a, double b)
{
    return ::taihe::make_holder<Shape, ::iface_test::IShape>(id, a, b);
}

::taihe::expected<::iface_test::CTest, ::taihe::error> createCTest(int32_t id)
{
    return taihe::make_holder<CTestImpl, ::iface_test::CTest>(id);
}

::taihe::expected<::iface_test::CTest, ::taihe::error> changeCTest(::iface_test::weak::CTest a)
{
    ::taihe::expected<int32_t, ::taihe::error> x = a->add(3, 4);
    if (x.has_value()) {
        return ::taihe::make_holder<CTestImpl, ::iface_test::CTest>(x.value());
    } else {
        return ::taihe::expected<::iface_test::CTest, ::taihe::error>(::taihe::unexpect, "Error in add");
    }
}

::taihe::expected<int32_t, ::taihe::error> multiply(int32_t a, int32_t b)
{
    return a * b;
}

::taihe::expected<::iface_test::IColor, ::taihe::error> makeIColor(::taihe::string_view id)
{
    // The parameters in the make_holder function should be of the same type
    // as the parameters in the constructor of the actual implementation class.
    return taihe::make_holder<Color, ::iface_test::IColor>(id);
}

::taihe::expected<void, ::taihe::error> copyIColor(::iface_test::weak::IColor a, ::iface_test::weak::IColor b)
{
    ::taihe::expected<::taihe::string, ::taihe::error> id = b->getId();
    if (id.has_value()) {
        a->setId(id.value());
        return {};
    } else {
        std::cout << "Error in getting ID " << id.error().message().c_str() << std::endl;
        return ::taihe::expected<void, ::taihe::error>(::taihe::unexpect, "Error in getting ID");
    }
}

::taihe::expected<::iface_test::IDerived, ::taihe::error> createIDerived()
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
