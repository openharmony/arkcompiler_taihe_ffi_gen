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

#include "iface_test.Foo.proj.2.hpp"
#include "stdexcept"
#include "taihe/string.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {

class Foo {
    ::taihe::string name_ {"foo"};

public:
    ::taihe::expected<void, ::taihe::error> Bar()
    {
        std::cout << "Fooimpl: " << __func__ << std::endl;
        return {};
    }

    ::taihe::expected<::taihe::string, ::taihe::error> GetName()
    {
        std::cout << "Fooimpl: " << __func__ << " " << name_ << std::endl;
        return name_;
    }

    ::taihe::expected<void, ::taihe::error> SetName(::taihe::string_view name)
    {
        std::cout << "Fooimpl: " << __func__ << " " << name << std::endl;
        name_ = name;
        return {};
    }
};

class BaseFunImpl {
public:
    BaseFunImpl()
    {
    }

    ::taihe::expected<::taihe::string, ::taihe::error> Base()
    {
        return "BaseFun.base";
    }

    ::taihe::expected<::taihe::string, ::taihe::error> Fun()
    {
        return "BaseFun.fun";
    }
};

class SubBaseFunImpl {
public:
    SubBaseFunImpl()
    {
    }

    ::taihe::expected<::taihe::string, ::taihe::error> Sub()
    {
        return "SubBaseFun.sub";
    }

    ::taihe::expected<::taihe::string, ::taihe::error> Base()
    {
        return "SubBaseFun.base";
    }

    ::taihe::expected<::taihe::string, ::taihe::error> Fun()
    {
        return "SubBaseFun.fun";
    }
};

class BaseElemImpl {
public:
    ::taihe::string base = "base";

    BaseElemImpl()
    {
    }

    ::taihe::expected<::taihe::string, ::taihe::error> GetBase()
    {
        return base;
    }

    ::taihe::expected<void, ::taihe::error> SetBase(::taihe::string_view s)
    {
        this->base = s;
        return {};
    }
};

class SubBaseElemImpl {
public:
    ::taihe::string base = "SubBaseElem";

    SubBaseElemImpl()
    {
    }

    ::taihe::expected<::taihe::string, ::taihe::error> Sub()
    {
        return "SubBaseElem.sub";
    }

    ::taihe::expected<::taihe::string, ::taihe::error> GetBase()
    {
        return base;
    }

    ::taihe::expected<void, ::taihe::error> SetBase(::taihe::string_view s)
    {
        this->base = s;
        return {};
    }
};

::taihe::expected<::iface_test::Foo, ::taihe::error> GetFooIface()
{
    std::cout << __func__ << std::endl;
    return make_holder<Foo, ::iface_test::Foo>();
}

::taihe::expected<::taihe::string, ::taihe::error> PrintFooName(::iface_test::weak::Foo foo)
{
    auto result = foo->GetName();
    if (result.has_value()) {
        auto name = result.value();
        std::cout << __func__ << ": " << name << std::endl;
        return name;
    }
    return "";
}

::taihe::expected<::iface_test::BaseFun, ::taihe::error> GetBaseFun()
{
    return taihe::make_holder<BaseFunImpl, ::iface_test::BaseFun>();
}

::taihe::expected<::iface_test::SubBaseFun, ::taihe::error> GetSubBaseFun()
{
    return taihe::make_holder<SubBaseFunImpl, ::iface_test::SubBaseFun>();
}

::taihe::expected<::iface_test::BaseElem, ::taihe::error> GetBaseElem()
{
    return taihe::make_holder<BaseElemImpl, ::iface_test::BaseElem>();
}

::taihe::expected<::iface_test::SubBaseElem, ::taihe::error> GetSubBaseElem()
{
    return taihe::make_holder<SubBaseElemImpl, ::iface_test::SubBaseElem>();
}

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

    ::taihe::expected<::taihe::string, ::taihe::error> GetId()
    {
        return id;
    }

    ::taihe::expected<void, ::taihe::error> SetId(::taihe::string_view s)
    {
        id = s;
        return {};
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

    ::taihe::expected<::taihe::string, ::taihe::error> GetId()
    {
        return id;
    }

    ::taihe::expected<void, ::taihe::error> SetId(::taihe::string_view s)
    {
        id = s;
        return {};
    }

    float CalculateArea()
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
    ::taihe::expected<void, ::taihe::error> Call()
    {
        std::cout << "derived call!" << std::endl;
        return {};
    }

    double CalculateArea()
    {
        return a * b;
    }

    ::taihe::expected<::taihe::string, ::taihe::error> GetId()
    {
        return id;
    }

    ::taihe::expected<void, ::taihe::error> SetId(::taihe::string_view s)
    {
        this->id = s;
        return {};
    }
};

::taihe::expected<::iface_test::IBase, ::taihe::error> MakeIBase(::taihe::string_view id)
{
    return ::taihe::make_holder<Base, ::iface_test::IBase>(id);
}

::taihe::expected<void, ::taihe::error> CopyIBase(::iface_test::weak::IBase a, ::iface_test::weak::IBase b)
{
    auto result = b->GetId();
    if (result.has_value()) {
        a->SetId(result.value());
    }
    return {};
}

::taihe::expected<::iface_test::IShape, ::taihe::error> MakeIShape(::taihe::string_view id, double a, double b)
{
    return ::taihe::make_holder<Shape, ::iface_test::IShape>(id, a, b);
}

::taihe::expected<::iface_test::IDerived, ::taihe::error> CreateIDerived()
{
    return taihe::make_holder<Derived, ::iface_test::IDerived>();
}

}  // namespace

TH_EXPORT_CPP_API_GetFooIface(GetFooIface);
TH_EXPORT_CPP_API_PrintFooName(PrintFooName);
TH_EXPORT_CPP_API_GetBaseFun(GetBaseFun);
TH_EXPORT_CPP_API_GetSubBaseFun(GetSubBaseFun);
TH_EXPORT_CPP_API_GetBaseElem(GetBaseElem);
TH_EXPORT_CPP_API_GetSubBaseElem(GetSubBaseElem);
TH_EXPORT_CPP_API_MakeIBase(MakeIBase);
TH_EXPORT_CPP_API_CopyIBase(CopyIBase);
TH_EXPORT_CPP_API_MakeIShape(MakeIShape);
TH_EXPORT_CPP_API_CreateIDerived(CreateIDerived);
// NOLINTEND
