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
        return ::taihe::expected<void, ::taihe::error>(::taihe::unexpect, "A Error in bar", 12);
    }

    int32_t bar_ii(int32_t a)
    {
        int32_t res = a + 1;
        return res;
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
    if (a >= 10) {
        return ::taihe::unexpected<::taihe::error>(::taihe::error("Index out of range", 10));
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
    std::cout << "catch error code in cpp bar " << res.error().code() << std::endl;
    return res.error().message();
}

::taihe::expected<void, ::taihe::error> callcb(::taihe::callback_view<void()> f)
{
    ::taihe::expected<void, ::taihe::error> res = f();
    if (!res.has_value()) {
        std::cout << "catch error in cpp callcb: " << res.error().message() << ", code: " << res.error().code_or(0)
                  << std::endl;
    }
    return res;
}

::taihe::expected<void, ::taihe::error> callcb_ii(::taihe::callback_view<int32_t(int32_t a)> f)
{
    ::taihe::expected<int32_t, ::taihe::error> res = f(1);
    if (res.has_value()) {
        std::cout << "success from callcb_ii: " << res.value() << std::endl;
    } else {
        std::cout << "catch error in cpp callcb_ii: " << res.error().message() << ", code: " << res.error().code_or(0)
                  << std::endl;
    }
    return {};
}
}  // namespace

TH_EXPORT_CPP_API_sayHello(sayHello);
TH_EXPORT_CPP_API_sayHello_ii(sayHello_ii);
TH_EXPORT_CPP_API_createFoo(createFoo);
TH_EXPORT_CPP_API_callFoo(callFoo);
TH_EXPORT_CPP_API_callcb(callcb);
TH_EXPORT_CPP_API_callcb_ii(callcb_ii);

// NOLINTEND
