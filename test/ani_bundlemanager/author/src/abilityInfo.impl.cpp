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
#include "abilityInfo.impl.hpp"
#include "abilityInfo.proj.hpp"
#include "metadata.h"
#include "skill.h"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace abilityInfo;

namespace {
// To be implemented.

class AbilityInfoImpl {
public:
    int32_t abilityInfoImpl = 506;

    AbilityInfoImpl()
    {
    }

    ::taihe::expected<string, ::taihe::error> GetBundleName()
    {
        return "abilityInfoImpl::getBundleName";
    }

    ::taihe::expected<string, ::taihe::error> GetModuleName()
    {
        return "abilityInfoImpl::getModuleName";
    }

    ::taihe::expected<string, ::taihe::error> GetName()
    {
        return "abilityInfoImpl::getName";
    }

    ::taihe::expected<string, ::taihe::error> GetLabel()
    {
        return "abilityInfoImpl::getLabel";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetLabelId()
    {
        return abilityInfoImpl;
    }

    ::taihe::expected<string, ::taihe::error> GetDescription()
    {
        return "abilityInfoImpl::getDescription";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetDescriptionId()
    {
        return abilityInfoImpl;
    }

    ::taihe::expected<string, ::taihe::error> GetIcon()
    {
        return "abilityInfoImpl::getIcon";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetIconId()
    {
        return abilityInfoImpl;
    }

    ::taihe::expected<string, ::taihe::error> GetProcess()
    {
        return "abilityInfoImpl::getProcess";
    }

    ::taihe::expected<bool, ::taihe::error> GetExported()
    {
        return true;
    }

    ::taihe::expected<::ohos::bundle::bundleManager::AbilityType, ::taihe::error> GetType()
    {
        return ::ohos::bundle::bundleManager::AbilityType::key_t::DATA;
    }

    ::taihe::expected<::ohos::bundle::bundleManager::DisplayOrientation, ::taihe::error> GetOrientation()
    {
        return ::ohos::bundle::bundleManager::DisplayOrientation::key_t::LANDSCAPE;
    }

    ::taihe::expected<::ohos::bundle::bundleManager::LaunchType, ::taihe::error> GetLaunchType()
    {
        return ::ohos::bundle::bundleManager::LaunchType::key_t::MULTITON;
    }

    ::taihe::expected<array<string>, ::taihe::error> GetPermissions()
    {
        array<string> res = {"abilityInfoImpl::getPermissions"};
        return res;
    }

    ::taihe::expected<string, ::taihe::error> GetReadPermission()
    {
        return "abilityInfoImpl::getReadPermission";
    }

    ::taihe::expected<string, ::taihe::error> GetWritePermission()
    {
        string res = "abilityInfoImpl::getWritePermission";
        return res;
    }

    ::taihe::expected<string, ::taihe::error> GetUri()
    {
        return "abilityInfoImpl::getUri";
    }

    ::taihe::expected<array<string>, ::taihe::error> GetDeviceTypes()
    {
        array<string> res = {"abilityInfoImpl::getDeviceTypes"};
        return res;
    }

    ::taihe::expected<array<::metadata::Metadata>, ::taihe::error> GetMetadata()
    {
        metadata::Metadata data = make_holder<MetadataImpl, metadata::Metadata>();
        array<metadata::Metadata> res = {data};
        return res;
    }

    ::taihe::expected<bool, ::taihe::error> GetEnabled()
    {
        return true;
    }

    ::taihe::expected<array<::ohos::bundle::bundleManager::SupportWindowMode>, ::taihe::error> GetSupportWindowModes()
    {
        array<::ohos::bundle::bundleManager::SupportWindowMode> res = {
            ::ohos::bundle::bundleManager::SupportWindowMode::key_t::FLOATING};

        return res;
    }

    ::taihe::expected<bool, ::taihe::error> GetExcludeFromDock()
    {
        return true;
    }

    ::taihe::expected<array<::skill::Skill>, ::taihe::error> GetSkills()
    {
        ::skill::Skill data = make_holder<SkillImpl, ::skill::Skill>();
        array<::skill::Skill> res = {data};

        return res;
    }

    ::taihe::expected<int32_t, ::taihe::error> GetAppIndex()
    {
        return abilityInfoImpl;
    }

    ::taihe::expected<int32_t, ::taihe::error> GetOrientationId()
    {
        return abilityInfoImpl;
    }
};

::taihe::expected<AbilityInfo, ::taihe::error> GetAbilityInfo()
{
    return make_holder<AbilityInfoImpl, AbilityInfo>();
}
}  // namespace

TH_EXPORT_CPP_API_GetAbilityInfo(GetAbilityInfo);
// NOLINTEND
