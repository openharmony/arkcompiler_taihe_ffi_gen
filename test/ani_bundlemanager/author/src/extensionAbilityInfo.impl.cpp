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
#include "extensionAbilityInfo.impl.hpp"
#include <iostream>
#include "extensionAbilityInfo.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace extensionAbilityInfo;

namespace {
// To be implemented.

class ExtensionAbilityInfoImpl {
public:
    int32_t extensionAbilityInfoImpl = 21474;

    ExtensionAbilityInfoImpl()
    {
    }

    ::taihe::expected<string, ::taihe::error> GetBundleName()
    {
        return "ExtensionAbilityInfoImpl::getBundleName";
    }

    ::taihe::expected<string, ::taihe::error> GetModuleName()
    {
        return "ExtensionAbilityInfoImpl::getModuleName";
    }

    ::taihe::expected<string, ::taihe::error> GetName()
    {
        return "ExtensionAbilityInfoImpl::getName";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetLabelId()
    {
        return extensionAbilityInfoImpl;
    }

    ::taihe::expected<int32_t, ::taihe::error> GetDescriptionId()
    {
        return extensionAbilityInfoImpl;
    }

    ::taihe::expected<int32_t, ::taihe::error> GetIconId()
    {
        return extensionAbilityInfoImpl;
    }

    ::taihe::expected<bool, ::taihe::error> GetExported()
    {
        return true;
    }

    ::taihe::expected<bool, ::taihe::error> GetExtensionAbilityTypeName()
    {
        return true;
    }

    ::taihe::expected<array<string>, ::taihe::error> GetPermissions()
    {
        array<string> str = {"ExtensionAbilityInfoImpl::getPermissions"};
        return str;
    }

    ::taihe::expected<bool, ::taihe::error> GetEnabled()
    {
        return true;
    }

    ::taihe::expected<string, ::taihe::error> GetReadPermission()
    {
        return "ExtensionAbilityInfoImpl::getReadPermission";
    }

    ::taihe::expected<string, ::taihe::error> GetWritePermission()
    {
        return "ExtensionAbilityInfoImpl::getWritePermission";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetAppIndex()
    {
        return extensionAbilityInfoImpl;
    }
};

::taihe::expected<ExtensionAbilityInfo, ::taihe::error> GetExtensionAbilityInfo()
{
    return make_holder<ExtensionAbilityInfoImpl, ExtensionAbilityInfo>();
}
}  // namespace

TH_EXPORT_CPP_API_GetExtensionAbilityInfo(GetExtensionAbilityInfo);
// NOLINTEND
