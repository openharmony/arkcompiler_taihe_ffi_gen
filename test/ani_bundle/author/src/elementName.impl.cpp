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
#include "elementName.impl.hpp"
#include "elementName.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace elementName;

namespace {
// To be implemented.

class ElementNameImpl {
public:
    optional<string> deviceId;
    string bundleName_ = "bundleName_";
    string abilityName_ = "abilityName_";
    optional<string> uri;
    optional<string> shortName;

    ElementNameImpl()
    {
    }

    ::taihe::expected<void, ::taihe::error> SetDevicedId(optional<string> deviceId)
    {
        this->deviceId = deviceId;
        return {};
    }

    ::taihe::expected<optional<string>, ::taihe::error> GetDevicedId()
    {
        return deviceId;
    }

    ::taihe::expected<void, ::taihe::error> SetBundleName(string_view bundleName)
    {
        bundleName_ = bundleName;
        return {};
    }

    ::taihe::expected<string, ::taihe::error> GetBundleName()
    {
        return bundleName_;
    }

    ::taihe::expected<void, ::taihe::error> SetAbilityName(string_view abilityName)
    {
        abilityName_ = abilityName;
        return {};
    }

    ::taihe::expected<string, ::taihe::error> GetAbilityName()
    {
        return abilityName_;
    }

    ::taihe::expected<void, ::taihe::error> SetUri(optional<string> uri)
    {
        this->uri = uri;
        return {};
    }

    ::taihe::expected<optional<string>, ::taihe::error> GetUri()
    {
        return uri;
    }

    ::taihe::expected<void, ::taihe::error> SetShortName(optional<string> shortName)
    {
        this->shortName = shortName;
        return {};
    }

    ::taihe::expected<optional<string>, ::taihe::error> GetShortName()
    {
        return shortName;
    }
};

::taihe::expected<ElementName, ::taihe::error> GetElementName()
{
    return make_holder<ElementNameImpl, ElementName>();
}
}  // namespace

TH_EXPORT_CPP_API_GetElementName(GetElementName);
// NOLINTEND
