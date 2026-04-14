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
#include <iostream>
#include "hapModuleInfo.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace hapModuleInfo;

namespace {
// To be implemented.

class HapModuleInfoImpl {
public:
    int32_t hapModuleInfoImpl = 21474;

    HapModuleInfoImpl()
    {
    }

    ::taihe::expected<string, ::taihe::error> GetName()
    {
        return "HapModuleInfoImpl::getName";
    }

    ::taihe::expected<string, ::taihe::error> GetIcon()
    {
        return "HapModuleInfoImpl::getIcon";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetIconId()
    {
        return hapModuleInfoImpl;
    }

    ::taihe::expected<string, ::taihe::error> GetLabel()
    {
        return "HapModuleInfoImpl::getLabel";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetLabelId()
    {
        return hapModuleInfoImpl;
    }

    ::taihe::expected<string, ::taihe::error> GetDescription()
    {
        return "HapModuleInfoImpl::getDescription";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetDescriptionId()
    {
        return hapModuleInfoImpl;
    }

    ::taihe::expected<string, ::taihe::error> GetMainElementName()
    {
        return "HapModuleInfoImpl::getMainElementName";
    }

    ::taihe::expected<array<string>, ::taihe::error> GetDeviceTypes()
    {
        array<string> str = {"HapModuleInfoImpl::getDeviceTypes"};
        return str;
    }

    ::taihe::expected<bool, ::taihe::error> GetInstallationFree()
    {
        return true;
    }

    ::taihe::expected<string, ::taihe::error> GetHashValue()
    {
        return "HapModuleInfoImpl::getHashValue";
    }

    ::taihe::expected<string, ::taihe::error> GetFileContextMenuConfig()
    {
        return "HapModuleInfoImpl::getFileContextMenuConfig";
    }

    ::taihe::expected<string, ::taihe::error> GetNativeLibraryPath()
    {
        return "HapModuleInfoImpl::getNativeLibraryPath";
    }

    ::taihe::expected<string, ::taihe::error> GetCodePath()
    {
        return "HapModuleInfoImpl::getCodePath";
    }
};

class DependencyImpl {
public:
    int32_t dependencyImpl = 21474;

    DependencyImpl()
    {
    }

    ::taihe::expected<string, ::taihe::error> GetModuleName()
    {
        return "HapModuleInfoImpl::getModuleName";
    }

    ::taihe::expected<string, ::taihe::error> GetBundleName()
    {
        return "HapModuleInfoImpl::getBundleName";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetVersionCode()
    {
        return dependencyImpl;
    }
};

class PreloadItemImpl {
public:
    PreloadItemImpl()
    {
    }

    ::taihe::expected<string, ::taihe::error> GetModuleName()
    {
        return "PreloadItemImpl::getModuleName";
    }
};

class RouterItemImpl {
public:
    RouterItemImpl()
    {
    }

    ::taihe::expected<string, ::taihe::error> GetName()
    {
        return "RouterItemImpl::getName";
    }

    ::taihe::expected<string, ::taihe::error> GetPageSourceFile()
    {
        return "RouterItemImpl::getPageSourceFile";
    }

    ::taihe::expected<string, ::taihe::error> GetBuildFunction()
    {
        return "RouterItemImpl::getBuildFunction";
    }

    ::taihe::expected<string, ::taihe::error> GetCustomData()
    {
        return "RouterItemImpl::getCustomData";
    }
};

class DataItemImpl {
public:
    DataItemImpl()
    {
    }

    ::taihe::expected<string, ::taihe::error> GetKey()
    {
        return "DataItemImpl::getKey";
    }

    ::taihe::expected<string, ::taihe::error> GetValue()
    {
        return "DataItemImpl::getValue";
    }
};

::taihe::expected<HapModuleInfo, ::taihe::error> GetHapModuleInfo()
{
    return make_holder<HapModuleInfoImpl, HapModuleInfo>();
}

::taihe::expected<Dependency, ::taihe::error> GetDependency()
{
    return make_holder<DependencyImpl, Dependency>();
}

::taihe::expected<PreloadItem, ::taihe::error> GetPreloadItem()
{
    return make_holder<PreloadItemImpl, PreloadItem>();
}

::taihe::expected<RouterItem, ::taihe::error> GetRouterItem()
{
    return make_holder<RouterItemImpl, RouterItem>();
}

::taihe::expected<DataItem, ::taihe::error> GetDataItem()
{
    return make_holder<DataItemImpl, DataItem>();
}
}  // namespace

TH_EXPORT_CPP_API_GetHapModuleInfo(GetHapModuleInfo);
TH_EXPORT_CPP_API_GetDependency(GetDependency);
TH_EXPORT_CPP_API_GetPreloadItem(GetPreloadItem);
TH_EXPORT_CPP_API_GetRouterItem(GetRouterItem);
TH_EXPORT_CPP_API_GetDataItem(GetDataItem);
// NOLINTEND
