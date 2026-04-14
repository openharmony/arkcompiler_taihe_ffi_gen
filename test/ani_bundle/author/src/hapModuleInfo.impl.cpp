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
#include "hapModuleInfo.impl.hpp"
#include "hapModuleInfo.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace hapModuleInfo;

namespace {

class HapModuleInfoImpl {
public:
    int32_t hapModuleInfoImpl = 1024;

    HapModuleInfoImpl()
    {
    }

    ::taihe::expected<string, ::taihe::error> GetName()
    {
        return "HapModuleInfo::getName";
    }

    ::taihe::expected<string, ::taihe::error> GetDescription()
    {
        return "HapModuleInfo::getDescription";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetDescriptionId()
    {
        return hapModuleInfoImpl;
    }

    ::taihe::expected<string, ::taihe::error> GetIcon()
    {
        return "HapModuleInfo::getIcon";
    }

    ::taihe::expected<string, ::taihe::error> GetLabel()
    {
        return "HapModuleInfo::getLabel";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetLabelId()
    {
        return hapModuleInfoImpl;
    }

    ::taihe::expected<int32_t, ::taihe::error> GetIconId()
    {
        return hapModuleInfoImpl;
    }

    ::taihe::expected<string, ::taihe::error> GetBackgroundImg()
    {
        return "HapModuleInfo::getBackgroundImg";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetSupportedModes()
    {
        return hapModuleInfoImpl;
    }

    ::taihe::expected<array<string>, ::taihe::error> GetReqCapabilities()
    {
        array<string> str = {"HapModuleInfo::getReqCapabilities"};
        return str;
    }

    ::taihe::expected<array<string>, ::taihe::error> GetDeviceTypes()
    {
        array<string> str = {"HapModuleInfo::getDeviceTypes"};
        return str;
    }

    ::taihe::expected<string, ::taihe::error> GetModuleName()
    {
        return "HapModuleInfo::getModuleName";
    }

    ::taihe::expected<string, ::taihe::error> GetMainAbilityName()
    {
        return "HapModuleInfo::getMainAbilityName";
    }

    ::taihe::expected<bool, ::taihe::error> GetInstallationFree()
    {
        return true;
    }
};

::taihe::expected<HapModuleInfo, ::taihe::error> GetHapModuleInfo()
{
    return make_holder<HapModuleInfoImpl, HapModuleInfo>();
}
}  // namespace

TH_EXPORT_CPP_API_GetHapModuleInfo(GetHapModuleInfo);
// NOLINTEND
