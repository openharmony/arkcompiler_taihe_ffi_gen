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
#include "on_off.impl.hpp"
#include "on_off.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace on_off;

namespace {
class ISetterObserverImpl {
public:
    ISetterObserverImpl()
    {
    }

    ::taihe::expected<void, ::taihe::error> onSet(callback_view<::taihe::expected<void, ::taihe::error>()> a)
    {
        a();
        std::cout << "IBase::onSet" << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> offSet(callback_view<::taihe::expected<void, ::taihe::error>()> a)
    {
        a();
        std::cout << "IBase::offSet" << std::endl;
        return {};
    }
};

::taihe::expected<ISetterObserver, ::taihe::error> getISetterObserver()
{
    return make_holder<ISetterObserverImpl, ISetterObserver>();
}

::taihe::expected<void, ::taihe::error> onFoo(callback_view<::taihe::expected<void, ::taihe::error>()> a)
{
    a();
    std::cout << "onFoo" << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> onBar(callback_view<::taihe::expected<void, ::taihe::error>()> a)
{
    a();
    std::cout << "onBar" << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> onBaz(int32_t a,
                                              callback_view<::taihe::expected<void, ::taihe::error>(int32_t)> cb)
{
    cb(a);
    std::cout << "onNewBaz" << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> offFoo(callback_view<::taihe::expected<void, ::taihe::error>()> a)
{
    a();
    std::cout << "offFoo" << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> offBar(callback_view<::taihe::expected<void, ::taihe::error>()> a)
{
    a();
    std::cout << "offBar" << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> offBaz(int32_t a,
                                               callback_view<::taihe::expected<void, ::taihe::error>(int32_t)> cb)
{
    cb(a);
    std::cout << "offNewBaz" << std::endl;
    return {};
}
}  // namespace

TH_EXPORT_CPP_API_getISetterObserver(getISetterObserver);
TH_EXPORT_CPP_API_onFoo(onFoo);
TH_EXPORT_CPP_API_onBar(onBar);
TH_EXPORT_CPP_API_onBaz(onBaz);
TH_EXPORT_CPP_API_offFoo(offFoo);
TH_EXPORT_CPP_API_offBar(offBar);
TH_EXPORT_CPP_API_offBaz(offBaz);
// NOLINTEND
