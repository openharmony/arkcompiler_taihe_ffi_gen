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
#include "ohos_bundle.impl.hpp"
#include <iomanip>
#include <iostream>
#include "ohos_bundle.proj.hpp"
#include "optional"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;

namespace {
// To be implemented.
class BundleOptionsImpl {
public:
    optional<int32_t> userId_;

    BundleOptionsImpl()
    {
    }

    ::taihe::expected<void, ::taihe::error> SetUserId(optional<int32_t> userId)
    {
        userId_ = userId;
        return {};
    }

    ::taihe::expected<optional<int32_t>, ::taihe::error> GetUserId()
    {
        return userId_;
    }
};

class OverloadInterfaceImpl {
public:
    optional<int32_t> id;

    OverloadInterfaceImpl()
    {
    }

    ::taihe::expected<void, ::taihe::error> GetApplicationInfo3param(string_view bundleName, int32_t bundleFlags,
                                                                     int32_t userId)
    {
        std::cout << bundleName + ":" << bundleFlags << ":" << userId << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> GetApplicationInfo2param(string_view bundleName, int32_t bundleFlags)
    {
        std::cout << bundleName + ":" << bundleFlags << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> GetApplicationInfoOptional(string_view bundleName, int32_t bundleFlags,
                                                                       optional_view<int32_t> userId)
    {
        id = userId;
        std::cout << bundleName + ":" << bundleFlags << ":" << id.value_or(0) << std::endl;
        return {};
    }
};

::taihe::expected<::ohos_bundle::OverloadInterface, ::taihe::error> Get_interface()
{
    return make_holder<OverloadInterfaceImpl, ::ohos_bundle::OverloadInterface>();
}

::taihe::expected<::ohos_bundle::BundleOptions, ::taihe::error> GetBundleOptions()
{
    return make_holder<BundleOptionsImpl, ::ohos_bundle::BundleOptions>();
}

::taihe::expected<void, ::taihe::error> GetBundleInfo(string_view bundleName, int32_t bundleFlags)
{
    std::cout << bundleName + ":" << bundleFlags << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> GetAbilityInfo(string_view bundleName, string_view abilityName)
{
    std::cout << bundleName + ":" << abilityName << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> GetApplicationInfo(string_view bundleName, int32_t bundleFlags, int32_t userId)
{
    std::cout << bundleName + ":" << bundleFlags << "," << userId << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> QueryAbilityByWant(int32_t bundleFlags, int32_t userId)
{
    std::cout << bundleFlags << "," << userId << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> GetAllBundleInfo(int32_t userId)
{
    std::cout << userId << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> GetAllApplicationInfo(int32_t bundleFlags, int32_t userId)
{
    std::cout << bundleFlags << "," << userId << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> GetNameForUid(int32_t uid)
{
    std::cout << uid << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> GetBundleArchiveInfo(string_view hapFilePath, int32_t bundleFlags)
{
    std::cout << hapFilePath << "," << bundleFlags << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> GetLaunchWantForBundle(string_view bundleName)
{
    std::cout << bundleName << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> GetAbilityLabel(string_view bundleName, string_view abilityName)
{
    std::cout << bundleName << "," << abilityName << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> GetAbilityIcon(string_view bundleName, string_view abilityName)
{
    std::cout << bundleName << "," << abilityName << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> IsAbilityEnabled()
{
    std::cout << "isAbilityEnabled" << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> IsApplicationEnabled(string_view bundleName)
{
    std::cout << bundleName << std::endl;
    return {};
}

}  // namespace

TH_EXPORT_CPP_API_GetBundleOptions(GetBundleOptions);
TH_EXPORT_CPP_API_GetBundleInfo(GetBundleInfo);
TH_EXPORT_CPP_API_GetAbilityInfo(GetAbilityInfo);
TH_EXPORT_CPP_API_Get_interface(Get_interface);
TH_EXPORT_CPP_API_QueryAbilityByWant(QueryAbilityByWant);
TH_EXPORT_CPP_API_GetAllBundleInfo(GetAllBundleInfo);
TH_EXPORT_CPP_API_GetAllApplicationInfo(GetAllApplicationInfo);
TH_EXPORT_CPP_API_GetNameForUid(GetNameForUid);
TH_EXPORT_CPP_API_GetBundleArchiveInfo(GetBundleArchiveInfo);
TH_EXPORT_CPP_API_GetLaunchWantForBundle(GetLaunchWantForBundle);
TH_EXPORT_CPP_API_GetAbilityLabel(GetAbilityLabel);
TH_EXPORT_CPP_API_GetAbilityIcon(GetAbilityIcon);
TH_EXPORT_CPP_API_IsAbilityEnabled(IsAbilityEnabled);
TH_EXPORT_CPP_API_IsApplicationEnabled(IsApplicationEnabled);
// NOLINTEND
