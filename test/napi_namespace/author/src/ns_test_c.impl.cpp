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

#include <iostream>
#include "my_module_b.functiontest.impl.hpp"
#include "my_module_b.functiontest.proj.hpp"

namespace {
class Base {
protected:
    ::taihe::string id;

public:
    Base(::taihe::string_view id) : id(id)
    {
        std::cout << "new base " << this << std::endl;
    }

    ~Base()
    {
        std::cout << "del base " << this << std::endl;
    }

    ::taihe::string getId()
    {
        return id;
    }

    void setId(::taihe::string_view s)
    {
        id = s;
        return;
    }
};

::my_module_b::functiontest::IBase makeIBase(::taihe::string_view id)
{
    return taihe::make_holder<Base, ::my_module_b::functiontest::IBase>(id);
}

void bar()
{
    std::cout << "namespace: my_module_b.functiontest, func: bar" << std::endl;
}
}  // namespace

TH_EXPORT_CPP_API_makeIBase(makeIBase);
TH_EXPORT_CPP_API_bar(bar);
// NOLINTEND
