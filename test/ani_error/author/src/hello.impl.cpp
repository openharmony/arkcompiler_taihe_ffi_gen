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
// Error codes
constexpr int32_t ERROR_CODE_BAR = 12;
constexpr int32_t ERROR_CODE_PROCESS_CALLBACK = 100;
constexpr int32_t ERROR_CODE_OUT_OF_RANGE = 10;

// Callback parameters
constexpr int32_t CALLBACK_PARAM_PROCESS = 10;
constexpr int32_t CALLBACK_PARAM_NOEXCEPT = 20;
constexpr int32_t CALLBACK_PARAM_VOID = 100;
constexpr int32_t CALLBACK_PARAM_NOEXCEPT_VOID = 200;
constexpr int32_t CALLBACK_PARAM_TEST_IV = 100;
constexpr int32_t CALLBACK_PARAM_TEST_II = 100;
constexpr int32_t CALLBACK_PARAM_GLOBAL_NOEXCEPT = 1;
constexpr int32_t CALLBACK_PARAM_CALLCB_II = 1;
constexpr int32_t CALLBACK_PARAM_GLOBAL_PARAM_NOEXCEPT = 400;

// Return values
constexpr int32_t RETURN_VALUE_PROCESS_VOID = 999;
constexpr int32_t RETURN_VALUE_BAR_RETURN = 555;
constexpr int32_t RETURN_VALUE_RETURN_NOEXCEPT = 666;
constexpr int32_t RETURN_VALUE_RETURN_VOID_CALLBACK = 888;
constexpr int32_t RETURN_VALUE_RETURN_VOID_NOEXCEPT_CALLBACK = 777;
constexpr int32_t RETURN_VALUE_BAR_VI = 123;
constexpr int32_t RETURN_VALUE_TEST_BAR_II_MULTIPLIER = 2;
constexpr int32_t RETURN_VALUE_TEST_BAR_VI = 456;
constexpr int32_t RETURN_VALUE_CALLCB = 100;
constexpr int32_t RETURN_VALUE_CALLCB_IV = 200;
constexpr int32_t RETURN_VALUE_TEST_CB_V = 0;
constexpr int32_t RETURN_VALUE_TEST_CB_VI = 1;
constexpr int32_t RETURN_VALUE_TEST_CB_IV = 2;
constexpr int32_t RETURN_VALUE_SAY_HELLO = 123;
constexpr int32_t RETURN_VALUE_GLOBAL_NOEXCEPT_CALLBACK = 111;
constexpr int32_t RETURN_VALUE_GETFOOVALUE = 42;

// Range limits
constexpr int32_t INDEX_RANGE_LIMIT = 10;

// Error messages
::taihe::string const ERROR_MESSAGE_BAR = "A Error in bar";
::taihe::string const ERROR_MESSAGE_OUT_OF_RANGE = "Index out of range";
::taihe::string const ERROR_MESSAGE_PROCESS_CALLBACK = "Error in processCallback";
::taihe::string const ERROR_MESSAGE_SYSTEM_INIT_FAILED = "System initialization failed";
::taihe::string const ERROR_MESSAGE_CANT_CATCH_BAR = "can't catch error in cpp bar";
::taihe::string const ERROR_MESSAGE_TRY_GET_VALUE = "try get value error";
::taihe::string const ERROR_MESSAGE_ERROR_VALUE = "error value";

class FooImpl {
public:
    ::taihe::expected<void, taihe::error> bar()
    {
        return ::taihe::expected<void, ::taihe::error>(::taihe::unexpect, ERROR_MESSAGE_BAR, ERROR_CODE_BAR);
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
        return RETURN_VALUE_GETFOOVALUE;
    }

    ::taihe::expected<int32_t, ::taihe::error> processCallback(
        ::taihe::callback_view<::taihe::expected<int32_t, ::taihe::error>(int32_t a)> f)
    {
        ::taihe::expected<int32_t, ::taihe::error> res = f(CALLBACK_PARAM_PROCESS);
        if (res.has_value()) {
            return res.value();
        } else {
            return ::taihe::unexpected<::taihe::error>(
                ::taihe::error(ERROR_MESSAGE_PROCESS_CALLBACK, ERROR_CODE_PROCESS_CALLBACK));
        }
    }

    int32_t processNoexceptCallback(::taihe::callback_view<int32_t(int32_t a)> f)
    {
        return f(CALLBACK_PARAM_NOEXCEPT);
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
        return RETURN_VALUE_PROCESS_VOID;
    }

    ::taihe::expected<void, ::taihe::error> barParam(int32_t a)
    {
        std::cout << "barParam called with: " << a << std::endl;
        return {};
    }

    ::taihe::expected<int32_t, ::taihe::error> barReturn()
    {
        return RETURN_VALUE_BAR_RETURN;
    }

    void processParamNoexcept(int32_t a)
    {
        std::cout << "processParamNoexcept called with: " << a << std::endl;
    }

    int32_t processReturnNoexcept()
    {
        return RETURN_VALUE_RETURN_NOEXCEPT;
    }

    ::taihe::expected<void, ::taihe::error> processParamVoidCallback(
        ::taihe::callback_view<::taihe::expected<void, ::taihe::error>(int32_t)> f)
    {
        f(CALLBACK_PARAM_VOID);
        return {};
    }

    ::taihe::expected<int32_t, ::taihe::error> processReturnVoidCallback()
    {
        return RETURN_VALUE_RETURN_VOID_CALLBACK;
    }

    void processParamVoidNoexceptCallback(::taihe::callback_view<void(int32_t)> f)
    {
        f(CALLBACK_PARAM_NOEXCEPT_VOID);
    }

    int32_t processReturnVoidNoexceptCallback()
    {
        return RETURN_VALUE_RETURN_VOID_NOEXCEPT_CALLBACK;
    }

    // Foo interface methods
    ::taihe::expected<void, ::taihe::error> bar_iv(int32_t a)
    {
        std::cout << "bar_iv called with: " << a << std::endl;
        return {};
    }

    ::taihe::expected<int32_t, ::taihe::error> bar_vi()
    {
        return RETURN_VALUE_BAR_VI;
    }

    void test_bar()
    {
        std::cout << "test_bar called" << std::endl;
    }

    int32_t test_bar_ii(int32_t a)
    {
        return a * RETURN_VALUE_TEST_BAR_II_MULTIPLIER;
    }

    void test_bar_iv(int32_t a)
    {
        std::cout << "test_bar_iv called with: " << a << std::endl;
    }

    int32_t test_bar_vi()
    {
        return RETURN_VALUE_TEST_BAR_VI;
    }

    ::taihe::expected<int32_t, ::taihe::error> callcb(
        ::taihe::callback_view<::taihe::expected<void, ::taihe::error>()> f)
    {
        ::taihe::expected<void, ::taihe::error> res = f();
        if (!res.has_value()) {
            std::cout << "catch error in callcb: " << res.error().message() << std::endl;
        }
        return RETURN_VALUE_CALLCB;
    }

    ::taihe::expected<int32_t, ::taihe::error> callcb_vi(
        ::taihe::callback_view<::taihe::expected<int32_t, ::taihe::error>()> f)
    {
        ::taihe::expected<int32_t, ::taihe::error> res = f();
        if (res.has_value()) {
            if (res.value() != RETURN_VALUE_TEST_CB_VI) {
                return ::taihe::expected<int32_t, ::taihe::error>(::taihe::unexpect, ERROR_MESSAGE_ERROR_VALUE);
            } else {
                std::cout << "success from callcb_vi: " << res.value() << std::endl;
            }
        } else {
            std::cout << "catch error in callcb_vi: " << res.error().message() << std::endl;
        }
        return res;
    }

    ::taihe::expected<int32_t, ::taihe::error> callcb_iv(
        ::taihe::callback_view<::taihe::expected<void, ::taihe::error>(int32_t)> f)
    {
        f(CALLBACK_PARAM_PROCESS);
        return RETURN_VALUE_CALLCB_IV;
    }

    ::taihe::expected<int32_t, ::taihe::error> callcb_ii(
        ::taihe::callback_view<::taihe::expected<int32_t, ::taihe::error>(int32_t)> f)
    {
        ::taihe::expected<int32_t, ::taihe::error> res = f(CALLBACK_PARAM_CALLCB_II);
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
        return RETURN_VALUE_TEST_CB_V;
    }

    int32_t test_cb_vi(::taihe::callback_view<void()> f)
    {
        f();
        return RETURN_VALUE_TEST_CB_VI;
    }

    int32_t test_cb_iv(::taihe::callback_view<void(int32_t)> f)
    {
        f(CALLBACK_PARAM_TEST_IV);
        return RETURN_VALUE_TEST_CB_IV;
    }

    int32_t test_cb_ii(::taihe::callback_view<int32_t(int32_t)> f)
    {
        return f(CALLBACK_PARAM_TEST_II);
    }
};

::taihe::expected<void, ::taihe::error> sayHello()
{
    bool success = false;

    if (success) {
        return {};
    } else {
        return ::taihe::expected<void, ::taihe::error>(::taihe::unexpect, ERROR_MESSAGE_SYSTEM_INIT_FAILED);
    }
}

::taihe::expected<int32_t, taihe::error> sayHello_ii(int32_t a)
{
    if (a >= INDEX_RANGE_LIMIT) {
        return ::taihe::unexpected<::taihe::error>(::taihe::error(ERROR_MESSAGE_OUT_OF_RANGE, ERROR_CODE_OUT_OF_RANGE));
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
    return RETURN_VALUE_SAY_HELLO;
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
        return ::taihe::expected<::taihe::string, ::taihe::error>(::taihe::unexpect, ERROR_MESSAGE_CANT_CATCH_BAR);
    }
    return ::taihe::expected<::taihe::string, ::taihe::error>(::taihe::unexpect, ERROR_MESSAGE_TRY_GET_VALUE);
}

::taihe::expected<int32_t, ::taihe::error> callcb(::taihe::callback_view<::taihe::expected<void, ::taihe::error>()> f)
{
    ::taihe::expected<void, ::taihe::error> res = f();
    if (!res.has_value()) {
        std::cout << "catch error in callcb: " << res.error().message() << std::endl;
    }
    return RETURN_VALUE_CALLCB;
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
    f(CALLBACK_PARAM_PROCESS);
    return RETURN_VALUE_CALLCB_IV;
}

::taihe::expected<int32_t, ::taihe::error> callcb_ii(
    ::taihe::callback_view<::taihe::expected<int32_t, ::taihe::error>(int32_t)> f)
{
    ::taihe::expected<int32_t, ::taihe::error> res = f(CALLBACK_PARAM_CALLCB_II);
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
    return RETURN_VALUE_TEST_CB_V;
}

int32_t test_cb_vi(::taihe::callback_view<void()> f)
{
    f();
    return RETURN_VALUE_TEST_CB_VI;
}

int32_t test_cb_iv(::taihe::callback_view<void(int32_t)> f)
{
    f(CALLBACK_PARAM_TEST_IV);
    return RETURN_VALUE_TEST_CB_IV;
}

int32_t test_cb_ii(::taihe::callback_view<int32_t(int32_t)> f)
{
    return f(CALLBACK_PARAM_TEST_II);
}

int32_t processGlobalVoidCallback(::taihe::callback_view<void()> f)
{
    f();
    return RETURN_VALUE_TEST_CB_V;
}

int32_t processGlobalNoexceptCallback(::taihe::callback_view<int32_t(int32_t)> f)
{
    return f(CALLBACK_PARAM_GLOBAL_NOEXCEPT);
}

int32_t processGlobalVoidNoexceptCallback(::taihe::callback_view<void()> f)
{
    f();
    return RETURN_VALUE_TEST_CB_V;
}

int32_t processGlobalParamNoexceptCallback(::taihe::callback_view<void(int32_t)> f)
{
    f(CALLBACK_PARAM_GLOBAL_PARAM_NOEXCEPT);
    return RETURN_VALUE_TEST_CB_V;
}

int32_t processGlobalReturnNoexceptCallback()
{
    return RETURN_VALUE_GLOBAL_NOEXCEPT_CALLBACK;
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
    return a * RETURN_VALUE_TEST_BAR_II_MULTIPLIER;
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
