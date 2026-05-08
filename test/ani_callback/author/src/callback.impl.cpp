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
#include "taihe/callback.hpp"
#include <iostream>
#include "callbackTest.impl.hpp"
#include "taihe/string.hpp"

using namespace taihe;

namespace {

class MyInterfaceImpl {
public:
    static int const ten = 10;
    static int const hundred = 100;
    static long long const tenBillion = 1000000000LL;

    MyInterfaceImpl()
    {
    }

    ::taihe::expected<::taihe::string, ::taihe::error> TestCbIntString(
        ::taihe::callback_view<::taihe::expected<void, ::taihe::error>(int8_t, int32_t)> f)
    {
        f(ten, hundred);
        return "testCbIntString";
    }

    ::taihe::expected<bool, ::taihe::error> TestCbIntBool(
        ::taihe::callback_view<::taihe::expected<void, ::taihe::error>(int16_t, int64_t)> f)
    {
        f(hundred, tenBillion);
        return true;
    }

    ::taihe::expected<::callbackTest::EnumData, ::taihe::error> TestCbEnum(
        ::taihe::callback_view<::taihe::expected<void, ::taihe::error>(int32_t)> f)
    {
        f(ten);
        return ::callbackTest::EnumData(::callbackTest::EnumData::key_t::F32_A);
    }
};

::taihe::expected<void, ::taihe::error> TestCbV(callback_view<::taihe::expected<void, ::taihe::error>()> f)
{
    f();
    return {};
}

::taihe::expected<void, ::taihe::error> TestCbI(callback_view<::taihe::expected<void, ::taihe::error>(int32_t)> f)
{
    static int const one = 1;
    f(one);
    return {};
}

::taihe::expected<void, ::taihe::error> TestCbS(
    callback_view<::taihe::expected<void, ::taihe::error>(string_view, bool)> f)
{
    f("hello", true);
    return {};
}

::taihe::expected<string, ::taihe::error> TestCbRs(
    callback_view<::taihe::expected<string, ::taihe::error>(string_view)> f)
{
    ::taihe::expected<string, ::taihe::error> out = f("hello");
    return out;
}

::taihe::expected<void, ::taihe::error> TestCbStruct(
    callback_view<::taihe::expected<::callbackTest::Data, ::taihe::error>(::callbackTest::Data const &)> f)
{
    ::taihe::expected<::callbackTest::Data, ::taihe::error> result = f(::callbackTest::Data {"a", "b", 1});
    return {};
}

::taihe::expected<::callbackTest::MyInterface, ::taihe::error> GetInterface()
{
    return taihe::make_holder<MyInterfaceImpl, ::callbackTest::MyInterface>();
}

using CallbackVoid = ::taihe::callback<::taihe::expected<void, ::taihe::error>()>;

::taihe::expected<CallbackVoid, ::taihe::error> GetCallbackVoid()
{
    taihe::string captured = "captured variable";
    return taihe::as_holder<CallbackVoid>([captured]() -> ::taihe::expected<void, ::taihe::error> {
        std::cout << "callback void called, captured: " << captured << std::endl;
        return {};
    });
}

using CallbackString = ::taihe::callback<::taihe::expected<taihe::string, ::taihe::error>()>;

::taihe::expected<CallbackString, ::taihe::error> GetCallbackString()
{
    taihe::string captured = "captured variable";
    return taihe::as_holder<CallbackString>([captured]() -> ::taihe::expected<taihe::string, ::taihe::error> {
        std::cout << "callback string called, captured: " << captured << std::endl;
        return "callback result: " + captured;
    });
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_TestCbV(TestCbV);
TH_EXPORT_CPP_API_TestCbI(TestCbI);
TH_EXPORT_CPP_API_TestCbS(TestCbS);
TH_EXPORT_CPP_API_TestCbRs(TestCbRs);
TH_EXPORT_CPP_API_TestCbStruct(TestCbStruct);
TH_EXPORT_CPP_API_GetInterface(GetInterface);
TH_EXPORT_CPP_API_GetCallbackVoid(GetCallbackVoid);
TH_EXPORT_CPP_API_GetCallbackString(GetCallbackString);
// NOLINTEND