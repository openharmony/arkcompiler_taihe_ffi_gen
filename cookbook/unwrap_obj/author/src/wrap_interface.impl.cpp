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
#include "wrap_interface.impl.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"
#include "wrap_interface.proj.hpp"

using namespace taihe;
using namespace wrap_interface;

namespace {
// 已经实现的类
class InnerFoo {
public:
    ::taihe::expected<string, ::taihe::error> func1() const
    {
        return "Hello from func1";
    }

    ::taihe::expected<string, ::taihe::error> func2() const
    {
        return "Hello from func2";
    }

    ::taihe::expected<void, ::taihe::error> setName(string str)
    {
        this->name = str;
        std::cout << "Inner Class's name is " << str << std::endl;
        return {};
    }

private:
    ::taihe::string name = "";
};

// Taihe interface 实现类
class FooImpl {
public:
    FooImpl()
    {
        m_data = new InnerFoo();
    }

    ::taihe::expected<int64_t, ::taihe::error> getInner()
    {
        return reinterpret_cast<int64_t>(this);
    }

    ::taihe::expected<string, ::taihe::error> func1()
    {
        return this->m_data->func1();
    }

    ::taihe::expected<string, ::taihe::error> func2()
    {
        return this->m_data->func2();
    }

private:
    friend ::taihe::expected<void, ::taihe::error> useFoo(weak::Foo);
    InnerFoo *m_data;
};

::taihe::expected<Foo, ::taihe::error> makeFoo()
{
    return make_holder<FooImpl, Foo>();
}

::taihe::expected<void, ::taihe::error> useFoo(weak::Foo obj)
{
    auto result1 = obj->func1();
    auto result2 = obj->func2();
    if (result1.has_value() && result2.has_value()) {
        std::cout << result1.value() << std::endl;
        std::cout << result2.value() << std::endl;
    }
    // 使用 getInner() 然后类型转换为 taihe 实现类指针
    reinterpret_cast<FooImpl *>(obj->getInner().value())->m_data->setName("Tom");
    return {};
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
TH_EXPORT_CPP_API_makeFoo(makeFoo);
TH_EXPORT_CPP_API_useFoo(useFoo);
// NOLINTEND
