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
#include "keep_name_test.impl.hpp"
#include "keep_name_test.proj.hpp"

#include "stdexcept"
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

    ::taihe::expected<void, ::taihe::error> OnSet(callback_view<::taihe::expected<void, ::taihe::error>()> a)
    {
        a();
        std::cout << "IBase::onSet" << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> OffSet(callback_view<::taihe::expected<void, ::taihe::error>()> a)
    {
        a();
        std::cout << "IBase::offSet" << std::endl;
        return {};
    }

private:
    string str;
    string new_str;
};

class Foo {
    string name_ {"foo"};

public:
    ::taihe::expected<void, ::taihe::error> Bar()
    {
        std::cout << "Fooimpl: " << __func__ << std::endl;
        return {};
    }

    ::taihe::expected<string, ::taihe::error> GetName()
    {
        std::cout << "Fooimpl: " << __func__ << " " << name_ << std::endl;
        return name_;
    }

    ::taihe::expected<void, ::taihe::error> SetName(string_view name)
    {
        std::cout << "Fooimpl: " << __func__ << " " << name << std::endl;
        name_ = name;
        return {};
    }
};

::taihe::expected<::keep_name_test::IBase, ::taihe::error> GetIBase(string_view a, string_view b)
{
    return make_holder<IBase, ::keep_name_test::IBase>(a, b);
}

::taihe::expected<::keep_name_test::Foo, ::taihe::error> GetFooIface()
{
    std::cout << __func__ << std::endl;
    return make_holder<Foo, ::keep_name_test::Foo>();
}

::taihe::expected<string, ::taihe::error> PrintFooName(::keep_name_test::weak::Foo foo)
{
    auto name = foo->GetName();
    if (name.has_value()) {
        std::cout << __func__ << ": " << name.value() << std::endl;
    }
    return name;
}

}  // namespace

// because these macros are auto-generate, lint will cause false positive.
TH_EXPORT_CPP_API_GetFooIface(GetFooIface);
TH_EXPORT_CPP_API_PrintFooName(PrintFooName);
TH_EXPORT_CPP_API_GetIBase(GetIBase);
// NOLINTEND
