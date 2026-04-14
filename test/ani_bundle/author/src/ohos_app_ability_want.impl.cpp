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
#include "ohos_app_ability_want.impl.hpp"
#include "ohos_app_ability_want.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace ohos_app_ability_want;

namespace {
// To be implemented.

class WantImpl {
public:
    optional<string> bundleName_;
    optional<string> abilityName_;
    optional<string> deviceId_;
    optional<string> uri_;
    optional<string> type_;
    optional<float> flags_;
    optional<string> action_;
    optional<array<string>> entities_;
    optional<string> moduleName_;
    optional<map<string, uintptr_t>> parameters_;

    WantImpl()
    {
    }

    ::taihe::expected<void, ::taihe::error> SetBundleName(optional_view<string> bundleName)
    {
        bundleName_ = bundleName;
        return {};
    }

    ::taihe::expected<optional<string>, ::taihe::error> GetBundleName()
    {
        return bundleName_;
    }

    ::taihe::expected<void, ::taihe::error> SetAbilityName(optional_view<string> abilityName)
    {
        abilityName_ = abilityName;
        return {};
    }

    ::taihe::expected<optional<string>, ::taihe::error> GetAbilityName()
    {
        return abilityName_;
    }

    ::taihe::expected<void, ::taihe::error> SetDeviceId(optional_view<string> deviceId)
    {
        deviceId_ = deviceId;
        return {};
    }

    ::taihe::expected<optional<string>, ::taihe::error> GetDeviceId()
    {
        return deviceId_;
    }

    ::taihe::expected<void, ::taihe::error> SetUri(optional_view<string> uri)
    {
        uri_ = uri;
        return {};
    }

    ::taihe::expected<optional<string>, ::taihe::error> GetUri()
    {
        return uri_;
    }

    ::taihe::expected<void, ::taihe::error> SetType(optional_view<string> type)
    {
        type_ = type;
        return {};
    }

    ::taihe::expected<optional<string>, ::taihe::error> GetType()
    {
        return type_;
    }

    ::taihe::expected<void, ::taihe::error> SetFlags(optional<float> flags)
    {
        flags_ = flags;
        return {};
    }

    ::taihe::expected<optional<float>, ::taihe::error> GetFlags()
    {
        return flags_;
    }

    ::taihe::expected<void, ::taihe::error> SetAction(optional_view<string> action)
    {
        action_ = action;
        return {};
    }

    ::taihe::expected<optional<string>, ::taihe::error> GetAction()
    {
        return action_;
    }

    ::taihe::expected<void, ::taihe::error> SetParameters(optional_view<map<string, uintptr_t>> parameters)
    {
        this->parameters_ = parameters;
        return {};
    }

    ::taihe::expected<optional<map<string, uintptr_t>>, ::taihe::error> GetParameters()
    {
        return parameters_;
    }

    ::taihe::expected<void, ::taihe::error> SetEntities(optional_view<array<string>> entities)
    {
        entities_ = entities;
        return {};
    }

    ::taihe::expected<optional<array<string>>, ::taihe::error> GetEntities()
    {
        return entities_;
    }

    ::taihe::expected<void, ::taihe::error> SetModuleName(optional_view<string> moduleName)
    {
        moduleName_ = moduleName;
        return {};
    }

    ::taihe::expected<optional<string>, ::taihe::error> GetModuleName()
    {
        return moduleName_;
    }
};

::taihe::expected<Want, ::taihe::error> CreateWant()
{
    return make_holder<WantImpl, Want>();
}
}  // namespace

TH_EXPORT_CPP_API_CreateWant(CreateWant);
// NOLINTEND
