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
#include "applicationInfo.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace applicationInfo;

namespace {
// To be implemented.

class ApplicationInfoImpl {
public:
    int32_t applicationInfoImpl = 21474;

    ApplicationInfoImpl()
    {
    }

    ::taihe::expected<string, ::taihe::error> GetName()
    {
        return "ApplicationInfoImpl::getName";
    }

    ::taihe::expected<string, ::taihe::error> GetDescription()
    {
        return "ApplicationInfoImpl::getDescription";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetDescriptionId()
    {
        return applicationInfoImpl;
    }

    ::taihe::expected<bool, ::taihe::error> GetEnabled()
    {
        return true;
    }

    ::taihe::expected<string, ::taihe::error> GetLabel()
    {
        return "ApplicationInfoImpl::getLabel";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetLabelId()
    {
        return applicationInfoImpl;
    }

    ::taihe::expected<string, ::taihe::error> GetIcon()
    {
        return "ApplicationInfoImpl::getIcon";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetIconId()
    {
        return applicationInfoImpl;
    }

    ::taihe::expected<string, ::taihe::error> GetProcess()
    {
        return "ApplicationInfoImpl::getProcess";
    }

    ::taihe::expected<array<string>, ::taihe::error> GetPermissions()
    {
        array<string> res = {"ApplicationInfoImpl::getPermissions"};
        return res;
    }

    ::taihe::expected<string, ::taihe::error> GetCodePath()
    {
        return "ApplicationInfoImpl::getCodePath";
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

    ::taihe::expected<string, ::taihe::error> GetAppDistributionType()
    {
        return "ApplicationInfoImpl::getAppDistributionType";
    }

    ::taihe::expected<string, ::taihe::error> GetAppProvisionType()
    {
        return "ApplicationInfoImpl::getAppProvisionType";
    }

    ::taihe::expected<bool, ::taihe::error> GetSystemApp()
    {
        return true;
    }

    ::taihe::expected<bool, ::taihe::error> GetDebug()
    {
        return true;
    }

    ::taihe::expected<bool, ::taihe::error> GetDataUnclearable()
    {
        return true;
    }

    ::taihe::expected<string, ::taihe::error> GetNativeLibraryPath()
    {
        return "ApplicationInfoImpl::getNativeLibraryPath";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetAppIndex()
    {
        return applicationInfoImpl;
    }

    ::taihe::expected<string, ::taihe::error> GetInstallSource()
    {
        return "ApplicationInfoImpl::getInstallSource";
    }

    ::taihe::expected<string, ::taihe::error> GetReleaseType()
    {
        return "ApplicationInfoImpl::getReleaseType";
    }

    ::taihe::expected<bool, ::taihe::error> GetCloudFileSyncEnabled()
    {
        return true;
    }
};

class ModuleMetadataImpl {
public:
    ModuleMetadataImpl()
    {
    }

    ::taihe::expected<string, ::taihe::error> GetModuleName()
    {
        return "ModuleMetadataImpl::getModuleName";
    }
};

class MultiAppModeImpl {
public:
    int32_t multiAppModeImpl = 21474;

    MultiAppModeImpl()
    {
    }

    ::taihe::expected<int32_t, ::taihe::error> GetMaxCount()
    {
        return multiAppModeImpl;
    }
};

::taihe::expected<ApplicationInfo, ::taihe::error> GetApplicationInfo()
{
    return make_holder<ApplicationInfoImpl, ApplicationInfo>();
}

::taihe::expected<ModuleMetadata, ::taihe::error> GetModuleMetadata()
{
    return make_holder<ModuleMetadataImpl, ModuleMetadata>();
}

::taihe::expected<MultiAppMode, ::taihe::error> GetMultiAppMode()
{
    return make_holder<MultiAppModeImpl, MultiAppMode>();
}
}  // namespace

TH_EXPORT_CPP_API_GetApplicationInfo(GetApplicationInfo);
TH_EXPORT_CPP_API_GetModuleMetadata(GetModuleMetadata);
TH_EXPORT_CPP_API_GetMultiAppMode(GetMultiAppMode);
// NOLINTEND
