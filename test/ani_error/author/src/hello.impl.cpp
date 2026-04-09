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

#include "hello.impl.hpp"
#include <cstdint>
#include <iostream>
#include <taihe/expected.hpp>
#include "hello.proj.hpp"

namespace {
class FooImpl {
public:
    ::taihe::expected<void, taihe::error> bar()
    {
        ::taihe::string ERROR_MESSAGE = "A Error in bar";
        constexpr int ERROR_CODE = 12;
        return ::taihe::expected<void, ::taihe::error>(::taihe::unexpect, ERROR_MESSAGE, ERROR_CODE);
    }

    ::taihe::expected<int32_t, ::taihe::error> bar_ii(int32_t a)
    {
        int32_t res = a + 1;
        return res;
    }

    ::taihe::string bar_ss(::taihe::string a)
    {
        return a + "_cpp";
    }

    int32_t getFooValue()
    {
        return 42;
    }

    ::taihe::expected<int32_t, ::taihe::error> processCallback(
        ::taihe::callback_view<::taihe::expected<int32_t, ::taihe::error>(int32_t a)> f)
    {
        ::taihe::expected<int32_t, ::taihe::error> res = f(10);
        if (res.has_value()) {
            return res.value();
        } else {
            return ::taihe::unexpected<::taihe::error>(::taihe::error("Error in processCallback", 100));
        }
    }

    int32_t processNoexceptCallback(::taihe::callback_view<int32_t(int32_t a)> f)
    {
        return f(20);
    }

    ::taihe::expected<void, ::taihe::error> processVoidCallback(
        ::taihe::callback_view<::taihe::expected<void, ::taihe::error>()> f)
    {
        ::taihe::expected<void, ::taihe::error> res = f();
        if (!res.has_value()) {
            std::cout << "catch error in processVoidCallback: " << res.error().message() << std::endl;
        }
        return res;
    }

    void processVoidNoexceptCallback(::taihe::callback_view<void()> f)
    {
        f();
    }

    void processNoexceptParam(int32_t a)
    {
        std::cout << "processNoexceptParam called with: " << a << std::endl;
    }

    void processNoexceptVoid()
    {
        std::cout << "processNoexceptVoid called" << std::endl;
    }

    void processParamVoid(int32_t a)
    {
        std::cout << "processParamVoid called with: " << a << std::endl;
    }

    ::taihe::expected<int32_t, ::taihe::error> processVoidReturn()
    {
        return 999;
    }

    ::taihe::expected<void, ::taihe::error> barParam(int32_t a)
    {
        std::cout << "barParam called with: " << a << std::endl;
        return {};
    }

    ::taihe::expected<int32_t, ::taihe::error> barReturn()
    {
        return 555;
    }

    void processParamNoexcept(int32_t a)
    {
        std::cout << "processParamNoexcept called with: " << a << std::endl;
    }

    int32_t processReturnNoexcept()
    {
        return 666;
    }

    ::taihe::expected<void, ::taihe::error> processParamVoidCallback(
        ::taihe::callback_view<::taihe::expected<void, ::taihe::error>(int32_t)> f)
    {
        f(100);
        return {};
    }

    ::taihe::expected<int32_t, ::taihe::error> processReturnVoidCallback()
    {
        return 888;
    }

    void processParamVoidNoexceptCallback(::taihe::callback_view<void(int32_t)> f)
    {
        f(200);
    }

    int32_t processReturnVoidNoexceptCallback()
    {
        return 777;
    }

    // Foo interface methods
    ::taihe::expected<void, ::taihe::error> bar_iv(int32_t a)
    {
        std::cout << "bar_iv called with: " << a << std::endl;
        return {};
    }

    ::taihe::expected<int32_t, ::taihe::error> bar_vi()
    {
        return 123;
    }

    void test_bar()
    {
        std::cout << "test_bar called" << std::endl;
    }

    int32_t test_bar_ii(int32_t a)
    {
        return a * 2;
    }

    void test_bar_iv(int32_t a)
    {
        std::cout << "test_bar_iv called with: " << a << std::endl;
    }

    int32_t test_bar_vi()
    {
        return 456;
    }

    ::taihe::expected<int32_t, ::taihe::error> callcb(
        ::taihe::callback_view<::taihe::expected<void, ::taihe::error>()> f)
    {
        ::taihe::expected<void, ::taihe::error> res = f();
        if (!res.has_value()) {
            std::cout << "catch error in callcb: " << res.error().message() << std::endl;
        }
        return 100;
    }

    ::taihe::expected<int32_t, ::taihe::error> callcb_vi(
        ::taihe::callback_view<::taihe::expected<int32_t, ::taihe::error>()> f)
    {
        ::taihe::expected<int32_t, ::taihe::error> res = f();
        if (res.has_value()) {
            std::cout << "success from callcb_vi: " << res.value() << std::endl;
        } else {
            std::cout << "catch error in callcb_vi: " << res.error().message() << std::endl;
        }
        return res;
    }

    ::taihe::expected<int32_t, ::taihe::error> callcb_iv(
        ::taihe::callback_view<::taihe::expected<void, ::taihe::error>(int32_t)> f)
    {
        f(10);
        return 200;
    }

    ::taihe::expected<int32_t, ::taihe::error> callcb_ii(
        ::taihe::callback_view<::taihe::expected<int32_t, ::taihe::error>(int32_t)> f)
    {
        ::taihe::expected<int32_t, ::taihe::error> res = f(1);
        if (res.has_value()) {
            std::cout << "success from callcb_ii: " << res.value() << std::endl;
        } else {
            std::cout << "catch error in callcb_ii: " << res.error().message() << std::endl;
        }
        return res;
    }

    int32_t test_cb_v(::taihe::callback_view<void()> f)
    {
        std::cout << "test_cb_v called" << std::endl;
        f();
        return 0;
    }

    int32_t test_cb_vi(::taihe::callback_view<void()> f)
    {
        f();
        return 1;
    }

    int32_t test_cb_iv(::taihe::callback_view<void(int32_t)> f)
    {
        f(100);
        return 2;
    }

    int32_t test_cb_ii(::taihe::callback_view<int32_t(int32_t)> f)
    {
        return f(100);
    }
};

::taihe::expected<void, ::taihe::error> sayHello()
{
    bool success = false;

    if (success) {
        return {};
    } else {
        return ::taihe::expected<void, ::taihe::error>(::taihe::unexpect, "System initialization failed");
    }
}

::taihe::expected<int32_t, taihe::error> sayHello_ii(int32_t a)
{
    int32_t range = 10;
    ::taihe::string ERROR_MESSAGE = "Index out of range";
    constexpr int32_t ERROR_CODE = 10;
    if (a >= range) {
        return ::taihe::unexpected<::taihe::error>(::taihe::error(ERROR_MESSAGE, ERROR_CODE));
    }
    return a;
}

::taihe::expected<void, ::taihe::error> sayHelloParam(int32_t a)
{
    std::cout << "sayHelloParam called with: " << a << std::endl;
    return {};
}

::taihe::expected<int32_t, ::taihe::error> sayHelloReturn()
{
    return 123;
}

::taihe::expected<::hello::Foo, ::taihe::error> createFoo()
{
    return taihe::make_holder<FooImpl, ::hello::Foo>();
}

::taihe::expected<::taihe::string, ::taihe::error> callFoo(::hello::weak::Foo a)
{
    ::taihe::expected<void, ::taihe::error> res = a->bar();
    if (!res.has_value()) {
        std::cout << "catch error code in cpp bar " << res.error().code() << " " << res.error().message() << std::endl;
        return res.error().message();
    } else {
        std::cout << "can't catch error code in cpp bar " << std::endl;
        return ::taihe::expected<::taihe::string, ::taihe::error>(::taihe::unexpect, "can't catch error in cpp bar");
    }
    return ::taihe::expected<::taihe::string, ::taihe::error>(::taihe::unexpect, "try get value error");
}

::taihe::expected<int32_t, ::taihe::error> callcb(::taihe::callback_view<::taihe::expected<void, ::taihe::error>()> f)
{
    ::taihe::expected<void, ::taihe::error> res = f();
    if (!res.has_value()) {
        std::cout << "catch error in callcb: " << res.error().message() << std::endl;
    }
    return 100;
}

::taihe::expected<int32_t, ::taihe::error> callcb_vi(
    ::taihe::callback_view<::taihe::expected<int32_t, ::taihe::error>()> f)
{
    ::taihe::expected<int32_t, ::taihe::error> res = f();
    if (res.has_value()) {
        std::cout << "success from callcb_vi: " << res.value() << std::endl;
    } else {
        std::cout << "catch error in callcb_vi: " << res.error().message() << std::endl;
    }
    return res;
}

::taihe::expected<int32_t, ::taihe::error> callcb_iv(
    ::taihe::callback_view<::taihe::expected<void, ::taihe::error>(int32_t)> f)
{
    f(10);
    return 200;
}

::taihe::expected<int32_t, ::taihe::error> callcb_ii(
    ::taihe::callback_view<::taihe::expected<int32_t, ::taihe::error>(int32_t)> f)
{
    ::taihe::expected<int32_t, ::taihe::error> res = f(1);
    if (res.has_value()) {
        std::cout << "success from callcb_ii: " << res.value() << std::endl;
    } else {
        std::cout << "catch error in callcb_ii: " << res.error().message() << std::endl;
    }
    return res;
}

int32_t test_cb_v(::taihe::callback_view<void()> f)
{
    std::cout << "test_cb_v called" << std::endl;
    f();
    return 0;
}

int32_t test_cb_vi(::taihe::callback_view<void()> f)
{
    f();
    return 1;
}

int32_t test_cb_iv(::taihe::callback_view<void(int32_t)> f)
{
    f(100);
    return 2;
}

int32_t test_cb_ii(::taihe::callback_view<int32_t(int32_t)> f)
{
    return f(100);
}

int32_t processGlobalVoidCallback(::taihe::callback_view<void()> f)
{
    f();
    return 0;
}

int32_t processGlobalNoexceptCallback(::taihe::callback_view<int32_t(int32_t)> f)
{
    return f(1);
}

int32_t processGlobalVoidNoexceptCallback(::taihe::callback_view<void()> f)
{
    f();
    return 0;
}

int32_t processGlobalParamNoexceptCallback(::taihe::callback_view<void(int32_t)> f)
{
    f(400);
    return 0;
}

int32_t processGlobalReturnNoexceptCallback()
{
    return 111;
}

void processGlobalNoexceptNoParamNoReturn()
{
    std::cout << "processGlobalNoexceptNoParamNoReturn called" << std::endl;
}

void processGlobalNoexceptParamNoReturn(int32_t a)
{
    std::cout << "processGlobalNoexceptParamNoReturn called with: " << a << std::endl;
}

int32_t processGlobalNoexceptParamReturn(int32_t a)
{
    return a * 2;
}
}  // namespace

TH_EXPORT_CPP_API_test_cb_v(test_cb_v);
TH_EXPORT_CPP_API_test_cb_vi(test_cb_vi);
TH_EXPORT_CPP_API_test_cb_iv(test_cb_iv);
TH_EXPORT_CPP_API_test_cb_ii(test_cb_ii);
TH_EXPORT_CPP_API_sayHello(sayHello);
TH_EXPORT_CPP_API_sayHello_ii(sayHello_ii);
TH_EXPORT_CPP_API_sayHelloParam(sayHelloParam);
TH_EXPORT_CPP_API_sayHelloReturn(sayHelloReturn);
TH_EXPORT_CPP_API_createFoo(createFoo);
TH_EXPORT_CPP_API_callFoo(callFoo);
TH_EXPORT_CPP_API_callcb(callcb);
TH_EXPORT_CPP_API_callcb_vi(callcb_vi);
TH_EXPORT_CPP_API_callcb_iv(callcb_iv);
TH_EXPORT_CPP_API_callcb_ii(callcb_ii);
TH_EXPORT_CPP_API_processGlobalVoidCallback(processGlobalVoidCallback);
TH_EXPORT_CPP_API_processGlobalNoexceptCallback(processGlobalNoexceptCallback);
TH_EXPORT_CPP_API_processGlobalVoidNoexceptCallback(processGlobalVoidNoexceptCallback);
TH_EXPORT_CPP_API_processGlobalParamNoexceptCallback(processGlobalParamNoexceptCallback);
TH_EXPORT_CPP_API_processGlobalReturnNoexceptCallback(processGlobalReturnNoexceptCallback);
TH_EXPORT_CPP_API_processGlobalNoexceptNoParamNoReturn(processGlobalNoexceptNoParamNoReturn);
TH_EXPORT_CPP_API_processGlobalNoexceptParamNoReturn(processGlobalNoexceptParamNoReturn);
TH_EXPORT_CPP_API_processGlobalNoexceptParamReturn(processGlobalNoexceptParamReturn);

// NOLINTEND
