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
#include "class_test.impl.hpp"

#include <iostream>

using namespace taihe;

namespace {
class UIAbility {
public:
    ::taihe::expected<void, ::taihe::error> onForeground()
    {
        std::cout << "in cpp onForeground" << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> onBackground()
    {
        std::cout << "in cpp onBackground" << std::endl;
        return {};
    }
};

::taihe::expected<::class_test::UIAbility, ::taihe::error> getUIAbility()
{
    return make_holder<UIAbility, ::class_test::UIAbility>();
}

::taihe::expected<void, ::taihe::error> useUIAbility(::class_test::weak::UIAbility a)
{
    a->onForeground();
    a->onBackground();
    return {};
}

::taihe::expected<void, ::taihe::error> logLifecycle(string_view str)
{
    std::cout << "[UIAbility]: " << str << std::endl;
    return {};
}

::taihe::expected<string, ::taihe::error> MyStructStaticFunc()
{
    return "Hello from MyStructStaticFunc";
}

class OldMyInterfaceImpl {
public:
    ::taihe::expected<::taihe::string, ::taihe::error> doSomething(string_view s)
    {
        return "Hello, " + std::string(s);
    }
};

::taihe::expected<::class_test::OldMyInterface, ::taihe::error> MyInterfaceCtor()
{
    return taihe::make_holder<OldMyInterfaceImpl, ::class_test::OldMyInterface>();
}

}  // namespace

TH_EXPORT_CPP_API_getUIAbility(getUIAbility);
TH_EXPORT_CPP_API_useUIAbility(useUIAbility);
TH_EXPORT_CPP_API_logLifecycle(logLifecycle);
TH_EXPORT_CPP_API_MyStructStaticFunc(MyStructStaticFunc);
TH_EXPORT_CPP_API_MyInterfaceCtor(MyInterfaceCtor);
// NOLINTEND
