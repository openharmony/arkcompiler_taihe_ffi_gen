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
#include "bundleInfo.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace bundleInfo;

namespace {
// To be implemented.

class ReqPermissionDetailImpl {
public:
    string name_ = "";
    string moduleName_ = "";
    string reason_ = "";
    int reasonId_ = 0;

    ReqPermissionDetailImpl()
    {
    }

    ::taihe::expected<void, ::taihe::error> SetName(string_view name)
    {
        this->name_ = name;
        return {};
    }

    ::taihe::expected<string, ::taihe::error> GetName()
    {
        return name_;
    }

    ::taihe::expected<void, ::taihe::error> SetModuleName(string_view moduleName)
    {
        this->moduleName_ = moduleName;
        return {};
    }

    ::taihe::expected<string, ::taihe::error> GetModuleName()
    {
        return moduleName_;
    }

    ::taihe::expected<void, ::taihe::error> SetReason(string_view reason)
    {
        this->reason_ = reason;
        return {};
    }

    ::taihe::expected<string, ::taihe::error> GetReason()
    {
        return reason_;
    }

    ::taihe::expected<void, ::taihe::error> SetReasonId(int32_t reasonId)
    {
        this->reasonId_ = reasonId;
        return {};
    }

    ::taihe::expected<int32_t, ::taihe::error> GetReasonId()
    {
        return reasonId_;
    }
};

class UsedSceneImpl {
public:
    array<string> abilities_ = {""};
    string when_ = "";

    UsedSceneImpl()
    {
    }

    ::taihe::expected<void, ::taihe::error> SetAbilities(array_view<string> abilities)
    {
        abilities_ = abilities;
        return {};
    }

    ::taihe::expected<array<string>, ::taihe::error> GetAbilities()
    {
        return abilities_;
    }

    ::taihe::expected<void, ::taihe::error> SetWhen(string_view when)
    {
        this->when_ = when;
        return {};
    }

    ::taihe::expected<string, ::taihe::error> GetWhen()
    {
        return when_;
    }
};

class SignatureInfoImpl {
public:
    SignatureInfoImpl()
    {
    }

    ::taihe::expected<string, ::taihe::error> GetAppId()
    {
        return "SignatureInfoImpl::getAppId";
    }

    ::taihe::expected<string, ::taihe::error> GetFingerprint()
    {
        return "SignatureInfoImpl::getFingerprint";
    }

    ::taihe::expected<string, ::taihe::error> GetAppIdentifier()
    {
        return "SignatureInfoImpl::getAppIdentifier";
    }

    ::taihe::expected<string, ::taihe::error> GetCertificate()
    {
        return "SignatureInfoImpl::getCertificate";
    }
};

class AppCloneIdentityImpl {
public:
    int32_t appCloneIdentityImpl = 21474;

    AppCloneIdentityImpl()
    {
    }

    ::taihe::expected<string, ::taihe::error> GetBundleName()
    {
        return "AppCloneIdentityImpl::getBundleName";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetAppIndex()
    {
        return appCloneIdentityImpl;
    }
};

class BundleInfoImpl {
public:
    int32_t version = 21474;

    BundleInfoImpl()
    {
    }

    ::taihe::expected<string, ::taihe::error> GetName()
    {
        return "BundleInfoImpl::getName";
    }

    ::taihe::expected<string, ::taihe::error> GetVendor()
    {
        return "BundleInfoImpl::getVendor";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetVersionCode()
    {
        return version;
    }

    ::taihe::expected<string, ::taihe::error> GetVersionName()
    {
        return "BundleInfoImpl::getVersionName";
    }

    ::taihe::expected<string, ::taihe::error> GetMinCompatibleVersionCode()
    {
        return "BundleInfoImpl::getMinCompatibleVersionCode";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetTargetVersion()
    {
        return version;
    }

    ::taihe::expected<int32_t, ::taihe::error> GetInstallTime()
    {
        return version;
    }

    ::taihe::expected<int32_t, ::taihe::error> GetUpdateTime()
    {
        return version;
    }

    ::taihe::expected<int32_t, ::taihe::error> GetAppIndex()
    {
        return version;
    }
};

::taihe::expected<BundleInfo, ::taihe::error> GetBundleInfo()
{
    return make_holder<BundleInfoImpl, BundleInfo>();
}

::taihe::expected<ReqPermissionDetail, ::taihe::error> GetReqPermissionDetail()
{
    return make_holder<ReqPermissionDetailImpl, ReqPermissionDetail>();
}

::taihe::expected<UsedScene, ::taihe::error> GetIUsedScene()
{
    return make_holder<UsedSceneImpl, UsedScene>();
}

::taihe::expected<SignatureInfo, ::taihe::error> GetISignatureInfo()
{
    return make_holder<SignatureInfoImpl, SignatureInfo>();
}

::taihe::expected<AppCloneIdentity, ::taihe::error> GetAppCloneIdentity()
{
    return make_holder<AppCloneIdentityImpl, AppCloneIdentity>();
}
}  // namespace

TH_EXPORT_CPP_API_GetBundleInfo(GetBundleInfo);
TH_EXPORT_CPP_API_GetReqPermissionDetail(GetReqPermissionDetail);
TH_EXPORT_CPP_API_GetIUsedScene(GetIUsedScene);
TH_EXPORT_CPP_API_GetISignatureInfo(GetISignatureInfo);
TH_EXPORT_CPP_API_GetAppCloneIdentity(GetAppCloneIdentity);
// NOLINTEND
