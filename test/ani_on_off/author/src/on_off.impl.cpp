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
#include "on_off.impl.hpp"

#include <iostream>

#include "on_off.IBase.proj.2.hpp"
#include "stdexcept"
#include "taihe/callback.hpp"
#include "taihe/string.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {
class IBase {
public:
    IBase(string a, string b) : str(a), new_str(b)
    {
    }

    ~IBase()
    {
    }

    ::taihe::expected<void, ::taihe::error> onSet(callback_view<::taihe::expected<void, ::taihe::error>()> a)
    {
        a();
        std::cout << "IBase::onSet" << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> offSet(callback_view<::taihe::expected<void, ::taihe::error>()> a)
    {
        a();
        std::cout << "IBase::offSet" << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> mytestNew()
    {
        TH_THROW(std::runtime_error, "mytestNew not implemented");
        return {};
    }

    ::taihe::expected<int32_t, ::taihe::error> onTest()
    {
        TH_THROW(std::runtime_error, "onTest not implemented");
    }

private:
    string str;
    string new_str;
};

class ColorImpl {
public:
    ColorImpl()
    {
        // Don't forget to implement the constructor.
    }

    ::taihe::expected<int32_t, ::taihe::error> add(int32_t a)
    {
        TH_THROW(std::runtime_error, "add not implemented");
    }
};

class BaseCls {
public:
    BaseCls()
    {
    }
};

::taihe::expected<::on_off::IBase, ::taihe::error> getIBase(string_view a, string_view b)
{
    return make_holder<IBase, ::on_off::IBase>(a, b);
}

::taihe::expected<int32_t, ::taihe::error> mytestGlobalnew()
{
    TH_THROW(std::runtime_error, "mytestGlobalnew not implemented");
}

::taihe::expected<int32_t, ::taihe::error> onGlobalnew()
{
    TH_THROW(std::runtime_error, "onGlobalnew not implemented");
}

::taihe::expected<void, ::taihe::error> onFoo(callback_view<::taihe::expected<void, ::taihe::error>()> a)
{
    a();
    std::cout << "onFoo" << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> onBar(callback_view<::taihe::expected<void, ::taihe::error>()> a)
{
    a();
    std::cout << "onBar" << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> onBaz(int32_t a, callback_view<::taihe::expected<void, ::taihe::error>()> cb)
{
    cb();
    std::cout << "a =" << a << ", onBaz" << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> offFoo(callback_view<::taihe::expected<void, ::taihe::error>()> a)
{
    a();
    std::cout << "offFoo" << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> offBar(callback_view<::taihe::expected<void, ::taihe::error>()> a)
{
    a();
    std::cout << "offBar" << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> offBaz(int32_t a, callback_view<::taihe::expected<void, ::taihe::error>()> cb)
{
    cb();
    std::cout << "offBaz" << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> onFooStatic(callback_view<::taihe::expected<void, ::taihe::error>()> a)
{
    a();
    std::cout << "onFooStatic" << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> offFooStatic(callback_view<::taihe::expected<void, ::taihe::error>()> a)
{
    a();
    std::cout << "offFooStatic" << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> onFuncI(callback_view<::taihe::expected<void, ::taihe::error>(int32_t)> a)
{
    int const i = 1;
    a(i);
    std::cout << "onFunI" << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> onFuncB(callback_view<::taihe::expected<void, ::taihe::error>(bool)> a)
{
    a(true);
    std::cout << "onFunB" << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> offFuncI(callback_view<::taihe::expected<void, ::taihe::error>(int32_t)> a)
{
    int const i = 1;
    a(i);
    std::cout << "offFunI" << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> offFuncB(callback_view<::taihe::expected<void, ::taihe::error>(bool)> a)
{
    a(true);
    std::cout << "offFunB" << std::endl;
    return {};
}
}  // namespace

// because these macros are auto-generate, lint will cause false positive.
TH_EXPORT_CPP_API_getIBase(getIBase);
TH_EXPORT_CPP_API_onFoo(onFoo);
TH_EXPORT_CPP_API_onBar(onBar);
TH_EXPORT_CPP_API_onBaz(onBaz);
TH_EXPORT_CPP_API_offFoo(offFoo);
TH_EXPORT_CPP_API_offBar(offBar);
TH_EXPORT_CPP_API_offBaz(offBaz);
TH_EXPORT_CPP_API_onFooStatic(onFooStatic);
TH_EXPORT_CPP_API_offFooStatic(offFooStatic);
TH_EXPORT_CPP_API_onFuncI(onFuncI);
TH_EXPORT_CPP_API_onFuncB(onFuncB);
TH_EXPORT_CPP_API_offFuncI(offFuncI);
TH_EXPORT_CPP_API_offFuncB(offFuncB);
TH_EXPORT_CPP_API_mytestGlobalnew(mytestGlobalnew);
TH_EXPORT_CPP_API_onGlobalnew(onGlobalnew);
// NOLINTEND
