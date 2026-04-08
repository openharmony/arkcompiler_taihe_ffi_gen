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

::taihe::expected<void, ::taihe::error> callcb(::taihe::callback_view<::taihe::expected<void, ::taihe::error>()> f)
{
    ::taihe::expected<void, ::taihe::error> res = f();
    if (!res.has_value()) {
        std::cout << "catch error in cpp callcb: " << res.error().message() << ", code: " << res.error().code()
                  << std::endl;
    }
    return res;
}

::taihe::expected<void, ::taihe::error> callcb_ii(
    ::taihe::callback_view<::taihe::expected<int32_t, ::taihe::error>(int32_t a)> f)
{
    ::taihe::expected<int32_t, ::taihe::error> res = f(1);
    if (res.has_value()) {
        std::cout << "success from callcb_ii: " << res.value() << std::endl;
    } else {
        std::cout << "catch error in cpp callcb_ii: " << res.error().message() << ", code: " << res.error().code()
                  << std::endl;
    }
    return {};
}

::taihe::expected<void, ::taihe::error> test_cb_v(::taihe::callback_view<void()> f)
{
    std::cout << "CPP impl test_cb_v " << std::endl;
    f();
    return {};
}

taihe::string ohos_concat_str(taihe::string_view a, taihe::string_view b)
{
    return a + b;
}
}  // namespace

TH_EXPORT_CPP_API_concat(ohos_concat_str);
TH_EXPORT_CPP_API_test_cb_v(test_cb_v);
TH_EXPORT_CPP_API_sayHello(sayHello);
TH_EXPORT_CPP_API_sayHello_ii(sayHello_ii);
TH_EXPORT_CPP_API_createFoo(createFoo);
TH_EXPORT_CPP_API_callFoo(callFoo);
TH_EXPORT_CPP_API_callcb(callcb);
TH_EXPORT_CPP_API_callcb_ii(callcb_ii);

// NOLINTEND
