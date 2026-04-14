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
#include "function_test.impl.hpp"

#include "function_test.Foo.proj.2.hpp"
#include "function_test.MyUnion.proj.1.hpp"
#include "stdexcept"
#include "taihe/optional.hpp"
#include "taihe/string.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {
class Foo {
public:
    ::taihe::expected<void, ::taihe::error> bar()
    {
        std::cout << "call bar" << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> bar_int(int32_t a)
    {
        std::cout << "call bar_int a is :" << a << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> bar_str(string_view a)
    {
        std::cout << "call bar_str a is :" << std::string(a) << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> bar_union(string_view a, ::function_test::MyUnion const &b)
    {
        std::cout << "call bar_union a is :" << std::string(a) << std::endl;
        switch (b.get_tag()) {
            case ::function_test::MyUnion::tag_t::sValue:
                std::cout << "s: " << b.get_sValue_ref() << std::endl;
                break;
            case ::function_test::MyUnion::tag_t::iValue:
                std::cout << "i: " << b.get_iValue_ref() << std::endl;
                break;
            case ::function_test::MyUnion::tag_t::fValue:
                std::cout << "f: " << b.get_fValue_ref() << std::endl;
                break;
        }
        return {};
    }

    ::taihe::expected<void, ::taihe::error> bar_union_opt(string_view a, optional_view<string> name)
    {
        std::cout << "call bar_union a is :" << std::string(a) << *name << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> test_cb_v(callback_view<::taihe::expected<void, ::taihe::error>()> f)
    {
        f();
        return {};
    }

    ::taihe::expected<void, ::taihe::error> test_cb_i(callback_view<::taihe::expected<void, ::taihe::error>(int32_t)> f)
    {
        f(1);
        return {};
    }

    ::taihe::expected<void, ::taihe::error> test_cb_s(
        callback_view<::taihe::expected<void, ::taihe::error>(string_view, bool)> f)
    {
        f("hello", true);
        return {};
    }

    ::taihe::expected<::taihe::string, ::taihe::error> test_cb_rs(
        callback_view<::taihe::expected<int64_t, ::taihe::error>(int64_t)> f)
    {
        auto result = f(444);
        if (result.has_value()) {
            return std::to_string(result.value());
        }
        return "";
    }

    ::taihe::expected<int32_t, ::taihe::error> addSync(int32_t a, int32_t b)
    {
        std::cout << "call addSync a and b is" << std::to_string(a) << std::to_string(b) << std::endl;
        return a + b;
    }
};

class FooCls {
public:
    ::taihe::expected<::taihe::string, ::taihe::error> get()
    {
        return "zhangsan";
    }
};

::taihe::expected<int32_t, ::taihe::error> static_func_add(int32_t a, int32_t b)
{
    return a + b;
}

::taihe::expected<int32_t, ::taihe::error> static_func_sub(int32_t a, int32_t b)
{
    return a - b;
}

::taihe::expected<::function_test::FooCls, ::taihe::error> getFooCls1(string_view name)
{
    return make_holder<FooCls, ::function_test::FooCls>();
}

::taihe::expected<::function_test::FooCls, ::taihe::error> getFooCls2(string_view name, string_view test)
{
    return make_holder<FooCls, ::function_test::FooCls>();
}

::taihe::expected<::function_test::Foo, ::taihe::error> makeFoo()
{
    return make_holder<Foo, ::function_test::Foo>();
}

static int32_t static_property = 0;

::taihe::expected<int32_t, ::taihe::error> getStaticProperty()
{
    return static_property;
}

::taihe::expected<void, ::taihe::error> setStaticProperty(int32_t a)
{
    static_property = a;
    return {};
}
}  // namespace

TH_EXPORT_CPP_API_static_func_add(static_func_add);
TH_EXPORT_CPP_API_static_func_sub(static_func_sub);
TH_EXPORT_CPP_API_getFooCls1(getFooCls1);
TH_EXPORT_CPP_API_getFooCls2(getFooCls2);
TH_EXPORT_CPP_API_makeFoo(makeFoo);
TH_EXPORT_CPP_API_setStaticProperty(setStaticProperty);
TH_EXPORT_CPP_API_getStaticProperty(getStaticProperty);
// NOLINTEND
