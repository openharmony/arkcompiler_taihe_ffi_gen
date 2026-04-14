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
#include "applicationInfo.impl.hpp"
#include <iostream>
#include "applicationInfo.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace applicationInfo;

namespace {
// To be implemented.

class ApplicationInfoImpl {
public:
    int32_t applicationInfoImpl = 102;

    ApplicationInfoImpl()
    {
    }

    ::taihe::expected<string, ::taihe::error> GetName()
    {
        return "ApplicationInfo::getName";
    }

    ::taihe::expected<string, ::taihe::error> GetDescription()
    {
        return "ApplicationInfo::getDescription";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetDescriptionId()
    {
        return applicationInfoImpl;
    }

    ::taihe::expected<bool, ::taihe::error> GetSystemApp()
    {
        return true;
    }

    ::taihe::expected<bool, ::taihe::error> GetEnabled()
    {
        return true;
    }

    ::taihe::expected<string, ::taihe::error> GetLabel()
    {
        return "ApplicationInfo::getLabel";
    }

    ::taihe::expected<string, ::taihe::error> GetLabelId()
    {
        return "ApplicationInfo::getLabelId";
    }

    ::taihe::expected<string, ::taihe::error> GetIcon()
    {
        return "ApplicationInfo::getIcon";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetIconId()
    {
        return applicationInfoImpl;
    }

    ::taihe::expected<string, ::taihe::error> GetProcess()
    {
        return "ApplicationInfo::getProcess";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetSupportedModes()
    {
        return applicationInfoImpl;
    }

    ::taihe::expected<array<string>, ::taihe::error> GetModuleSourceDirs()
    {
        array<string> str = {"ApplicationInfo::getProcess"};
        return str;
    }

    ::taihe::expected<array<string>, ::taihe::error> GetPermissions()
    {
        array<string> str = {"ApplicationInfo::getPermissions"};
        return str;
    }

    ::taihe::expected<string, ::taihe::error> GetEntryDir()
    {
        return "ApplicationInfo::getEntryDir";
    }

    ::taihe::expected<string, ::taihe::error> GetCodePath()
    {
        return "ApplicationInfo::getCodePath";
    }

    ::taihe::expected<bool, ::taihe::error> GetRemovable()
    {
        return true;
    }

    ::taihe::expected<int32_t, ::taihe::error> GetAccessTokenId()
    {
        return applicationInfoImpl;
    }

    ::taihe::expected<int32_t, ::taihe::error> GetUid()
    {
        return applicationInfoImpl;
    }

    ::taihe::expected<string, ::taihe::error> GetEntityType()
    {
        return "ApplicationInfo::getEntityType";
    }
};

::taihe::expected<ApplicationInfo, ::taihe::error> GetApplicationInfo()
{
    return make_holder<ApplicationInfoImpl, ApplicationInfo>();
}
}  // namespace

TH_EXPORT_CPP_API_GetApplicationInfo(GetApplicationInfo);
// NOLINTEND
