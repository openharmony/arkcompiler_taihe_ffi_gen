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
#include "bundleInfo.impl.hpp"
#include <iostream>
#include "bundleInfo.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace bundleInfo;

namespace {
// To be implemented.

class UsedSceneImpl {
public:
    string when_ = "test";
    array<string> abilities_ = {"getAbilities", "not", "implemented"};

    UsedSceneImpl()
    {
    }

    ::taihe::expected<array<string>, ::taihe::error> GetAbilities()
    {
        return abilities_;
    }

    ::taihe::expected<void, ::taihe::error> SetAbilities(array_view<string> abilities)
    {
        abilities_ = abilities;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> SetWhen(string_view when)
    {
        when_ = when;
        return {};
    }

    ::taihe::expected<string, ::taihe::error> GetWhen()
    {
        return when_;
    }
};

class ReqPermissionDetailImpl {
public:
    string name_ = "name";
    string reason_ = "reason_";
    UsedSceneImpl usedSceneImpl_;

    ReqPermissionDetailImpl()
    {
    }

    ::taihe::expected<string, ::taihe::error> GetName()
    {
        return name_;
    }

    ::taihe::expected<void, ::taihe::error> SetName(string_view name)
    {
        name_ = name;
        return {};
    }

    ::taihe::expected<string, ::taihe::error> GetReason()
    {
        return reason_;
    }

    ::taihe::expected<void, ::taihe::error> SetReason(string_view reason)
    {
        reason_ = reason;
        return {};
    }

    ::taihe::expected<UsedSceneImpl, ::taihe::error> GetUsedScene()
    {
        return GetUsedScene();
    }

    ::taihe::expected<void, ::taihe::error> SetUsedScene(UsedSceneImpl usedScene)
    {
        usedSceneImpl_.when_ = usedScene.when_;
        usedSceneImpl_.abilities_ = usedScene.abilities_;
        return {};
    }
};

class BundleInfoImpl {
public:
    int32_t bundleInfoImpl = 127;

    BundleInfoImpl()
    {
    }

    ::taihe::expected<string, ::taihe::error> GetName()
    {
        return "bundleInfo::getName";
    }

    ::taihe::expected<string, ::taihe::error> GetType()
    {
        return "bundleInfo::getType";
    }

    ::taihe::expected<string, ::taihe::error> GetAppId()
    {
        return "bundleInfo::getAppId";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetUid()
    {
        return bundleInfoImpl;
    }

    ::taihe::expected<int32_t, ::taihe::error> GetInstallTime()
    {
        return bundleInfoImpl;
    }

    ::taihe::expected<int32_t, ::taihe::error> GetUpdateTime()
    {
        return bundleInfoImpl;
    }

    ::taihe::expected<array<string>, ::taihe::error> GetReqPermissions()
    {
        array<string> str = {"bundleInfo::getReqPermissions"};
        return str;
    }

    ::taihe::expected<string, ::taihe::error> GetVendor()
    {
        return "bundleInfo::getVendor";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetVersionCode()
    {
        return bundleInfoImpl;
    }

    ::taihe::expected<string, ::taihe::error> GetVersionName()
    {
        return "bundleInfo::getVersionName";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetCompatibleVersion()
    {
        return bundleInfoImpl;
    }

    ::taihe::expected<int32_t, ::taihe::error> GetTargetVersion()
    {
        return bundleInfoImpl;
    }

    ::taihe::expected<bool, ::taihe::error> GetIsCompressNativeLibs()
    {
        return true;
    }

    ::taihe::expected<string, ::taihe::error> GetEntryModuleName()
    {
        return "bundleInfo::getEntryModuleName";
    }

    ::taihe::expected<string, ::taihe::error> GetCpuAbi()
    {
        return "bundleInfo::getCpuAbi";
    }

    ::taihe::expected<string, ::taihe::error> GetIsSilentInstallation()
    {
        return "bundleInfo::getIsSilentInstallation";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetMinCompatibleVersionCode()
    {
        return bundleInfoImpl;
    }

    ::taihe::expected<bool, ::taihe::error> GetEntryInstallationFree()
    {
        return true;
    }

    ::taihe::expected<array<int32_t>, ::taihe::error> GetReqPermissionStates()
    {
        array<int32_t> arr = {bundleInfoImpl};
        return arr;
    }
};

::taihe::expected<UsedScene, ::taihe::error> GetUsedScene()
{
    return make_holder<UsedSceneImpl, UsedScene>();
}

::taihe::expected<ReqPermissionDetail, ::taihe::error> GetReqPermissionDetail()
{
    return make_holder<ReqPermissionDetailImpl, ReqPermissionDetail>();
}

::taihe::expected<BundleInfo, ::taihe::error> GetBundleInfo()
{
    return make_holder<BundleInfoImpl, BundleInfo>();
}
}  // namespace

TH_EXPORT_CPP_API_GetUsedScene(GetUsedScene);
TH_EXPORT_CPP_API_GetReqPermissionDetail(GetReqPermissionDetail);
TH_EXPORT_CPP_API_GetBundleInfo(GetBundleInfo);
// NOLINTEND
