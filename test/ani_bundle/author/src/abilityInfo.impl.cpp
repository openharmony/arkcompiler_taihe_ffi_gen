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
#include "abilityInfo.impl.hpp"
#include "abilityInfo.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"
using namespace taihe;
using namespace abilityInfo;

namespace {
// To be implemented.

class AbilityInfoImpl {
public:
    int32_t abilityInfoImpl = 100;

    AbilityInfoImpl()
    {
    }

    ::taihe::expected<::taihe::string, ::taihe::error> GetBundleName()
    {
        return "AbilityInfo::getBundleName";
    }

    ::taihe::expected<::taihe::string, ::taihe::error> GetName()
    {
        return "AbilityInfo::getName";
    }

    ::taihe::expected<::taihe::string, ::taihe::error> GetLabel()
    {
        return "AbilityInfo::getLabel";
    }

    ::taihe::expected<::taihe::string, ::taihe::error> GetDescription()
    {
        return "AbilityInfo::getDescription";
    }

    ::taihe::expected<::taihe::string, ::taihe::error> GetIcon()
    {
        return "AbilityInfo::getIcon";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetLabelId()
    {
        return abilityInfoImpl;
    }

    ::taihe::expected<int32_t, ::taihe::error> GetDescriptionId()
    {
        return abilityInfoImpl;
    }

    ::taihe::expected<int32_t, ::taihe::error> GetIconId()
    {
        return abilityInfoImpl;
    }

    ::taihe::expected<::taihe::string, ::taihe::error> GetModuleName()
    {
        return "AbilityInfo::getModuleName";
    }

    ::taihe::expected<::taihe::string, ::taihe::error> GetProcess()
    {
        return "AbilityInfo::getProcess";
    }

    ::taihe::expected<::taihe::string, ::taihe::error> GetTargetAbility()
    {
        return "AbilityInfo::getTargetAbility";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetBackgroundModes()
    {
        return abilityInfoImpl;
    }

    ::taihe::expected<bool, ::taihe::error> GetIsVisible()
    {
        return true;
    }

    ::taihe::expected<bool, ::taihe::error> GetFormEnabled()
    {
        return true;
    }

    ::taihe::expected<array<string>, ::taihe::error> GetPermissions()
    {
        array<string> str = {"AbilityInfo::getTargetAbility"};
        return str;
    }

    ::taihe::expected<array<string>, ::taihe::error> GetDeviceTypes()
    {
        array<string> str = {"AbilityInfo::getDeviceTypes"};
        return str;
    }

    ::taihe::expected<array<string>, ::taihe::error> GetDeviceCapabilities()
    {
        array<string> str = {"AbilityInfo::getDeviceCapabilities"};
        return str;
    }

    ::taihe::expected<::taihe::string, ::taihe::error> GetReadPermission()
    {
        return "AbilityInfo::getReadPermission";
    }

    ::taihe::expected<::taihe::string, ::taihe::error> GetWritePermission()
    {
        return "AbilityInfo::getWritePermission";
    }

    ::taihe::expected<::taihe::string, ::taihe::error> GetUri()
    {
        return "AbilityInfo::getUri";
    }

    ::taihe::expected<bool, ::taihe::error> GetEnabled()
    {
        return true;
    }
};

::taihe::expected<AbilityInfo, ::taihe::error> GetAbilityInfo()
{
    return make_holder<AbilityInfoImpl, AbilityInfo>();
}
}  // namespace

TH_EXPORT_CPP_API_GetAbilityInfo(GetAbilityInfo);
// NOLINTEND
