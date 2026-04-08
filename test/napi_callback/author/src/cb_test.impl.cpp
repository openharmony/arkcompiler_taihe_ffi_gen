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

#include "cb_test.impl.hpp"
#include <iostream>
#include "cb_test.proj.hpp"
#include "taihe/callback.hpp"
#include "taihe/expected.hpp"
#include "taihe/string.hpp"

namespace {
::taihe::expected<void, ::taihe::error> test_cb_v(::taihe::callback_view<::taihe::expected<void, ::taihe::error>()> f)
{
    std::cout << "CPP impl test_cb_v " << std::endl;
    f();
    return {};
}

::taihe::expected<void, ::taihe::error> test_cb_i(
    ::taihe::callback_view<::taihe::expected<void, ::taihe::error>(int32_t)> f)
{
    std::cout << "CPP impl test_cb_i " << std::endl;
    f(1);
    return {};
}

::taihe::expected<void, ::taihe::error> test_cb_s(
    ::taihe::callback_view<::taihe::expected<void, ::taihe::error>(::taihe::string_view, bool)> f)
{
    std::cout << "CPP impl test_cb_s " << std::endl;
    f("hello", true);
    return {};
}

::taihe::expected<::taihe::string, ::taihe::error> test_cb_rs(
    ::taihe::callback_view<::taihe::expected<::taihe::string, ::taihe::error>(::taihe::string_view)> f)
{
    ::taihe::expected<::taihe::string, ::taihe::error> res_expected = f("hello");
    if (res_expected.has_value()) {
        ::taihe::string out = res_expected.value();
        std::cout << "CPP impl test_cb_rs: " << out << std::endl;
        return out;
    } else {
        return ::taihe::unexpected<::taihe::error>(res_expected.error());
    }
}

::taihe::expected<void, ::taihe::error> test_cb_struct(
    ::taihe::callback_view<::taihe::expected<::cb_test::Data, ::taihe::error>(::cb_test::Data const &)> f)
{
    ::taihe::expected<::cb_test::Data, ::taihe::error> res_expected = f(::cb_test::Data {"a", "b", 1});
    if (res_expected.has_value()) {
        ::cb_test::Data result = res_expected.value();
        std::cout << "CPP impl test_cb_struct " << result.a << " " << result.b << " " << result.c << std::endl;
        return {};
    } else {
        return ::taihe::unexpected<::taihe::error>(res_expected.error());
    }
}

class CallbackAImpl {
public:
    CallbackAImpl()
    {
    }

    ::taihe::expected<::taihe::string, ::taihe::error> operator()(::taihe::string_view a)
    {
        std::cout << a << std::endl;
        return "CallbackReverse";
    }
};

::taihe::expected<::taihe::callback<::taihe::expected<::taihe::string, ::taihe::error>(::taihe::string_view a)>,
                  ::taihe::error>
test_x(::taihe::callback_view<::taihe::expected<void, ::taihe::error>()> f)
{
    f();
    return ::taihe::make_holder<
        CallbackAImpl, ::taihe::callback<::taihe::expected<::taihe::string, ::taihe::error>(::taihe::string_view a)>>();
}

class MyInterfaceImpl {
public:
    static int const ten = 10;
    static int const hundred = 100;

    ::taihe::expected<::taihe::string, ::taihe::error> testCbIntString(
        ::taihe::callback_view<::taihe::expected<void, ::taihe::error>(int32_t, int32_t)> f)
    {
        f(ten, hundred);
        return "testCbIntString";
    }

    ::taihe::expected<bool, ::taihe::error> testCbIntBool(
        ::taihe::callback_view<::taihe::expected<void, ::taihe::error>(int32_t, int32_t)> f)
    {
        f(hundred, hundred);
        return true;
    }

    ::taihe::expected<::cb_test::EnumData, ::taihe::error> testCbEnum(
        ::taihe::callback_view<::taihe::expected<::cb_test::EnumData, ::taihe::error>(::cb_test::EnumData)> f)
    {
        return f(::cb_test::EnumData(::cb_test::EnumData::key_t::F32_A));
    }
};

::taihe::expected<::cb_test::MyInterface, ::taihe::error> getInterface()
{
    return taihe::make_holder<MyInterfaceImpl, ::cb_test::MyInterface>();
}

::taihe::expected<::taihe::string, ::taihe::error> test_cb_iface(
    ::taihe::callback_view<::taihe::expected<::cb_test::MyInterface, ::taihe::error>(::cb_test::weak::MyInterface a)> f)
{
    auto res = f(taihe::make_holder<MyInterfaceImpl, ::cb_test::MyInterface>());
    return "test_cb_iface";
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
TH_EXPORT_CPP_API_test_cb_v(test_cb_v);
TH_EXPORT_CPP_API_test_cb_i(test_cb_i);
TH_EXPORT_CPP_API_test_cb_s(test_cb_s);
TH_EXPORT_CPP_API_test_cb_rs(test_cb_rs);
TH_EXPORT_CPP_API_test_cb_struct(test_cb_struct);
TH_EXPORT_CPP_API_test_x(test_x);
TH_EXPORT_CPP_API_getInterface(getInterface);
TH_EXPORT_CPP_API_test_cb_iface(test_cb_iface);
// NOLINTEND
