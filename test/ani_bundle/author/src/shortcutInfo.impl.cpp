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
#include "shortcutInfo.impl.hpp"
#include "shortcutInfo.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace shortcutInfo;

namespace {
// To be implemented.

class ShortcutInfoImpl {
public:
    int32_t shortcutInfoImpl = 4096;

    ShortcutInfoImpl()
    {
    }

    ::taihe::expected<string, ::taihe::error> GetId()
    {
        return "ShortcutInfo::GetId";
    }

    ::taihe::expected<string, ::taihe::error> GetBundleName()
    {
        return "ShortcutInfo::GetBundleName";
    }

    ::taihe::expected<string, ::taihe::error> GetHostAbility()
    {
        return "ShortcutInfo::GetHostAbility";
    }

    ::taihe::expected<string, ::taihe::error> GetIcon()
    {
        return "ShortcutInfo::GetIcon";
    }

    ::taihe::expected<string, ::taihe::error> GetLabel()
    {
        return "ShortcutInfo::GetLabel";
    }

    ::taihe::expected<int32_t, ::taihe::error> GetLabelId()
    {
        return shortcutInfoImpl;
    }

    ::taihe::expected<int32_t, ::taihe::error> GetIconId()
    {
        return shortcutInfoImpl;
    }

    ::taihe::expected<string, ::taihe::error> GetDisableMessage()
    {
        return "ShortcutInfo::GetDisableMessage";
    }

    ::taihe::expected<optional<bool>, ::taihe::error> GetIsStatic()
    {
        return optional<bool>::make(true);
    }

    ::taihe::expected<optional<bool>, ::taihe::error> GetIsHomeShortcut()
    {
        return optional<bool>::make(true);
    }

    ::taihe::expected<optional<bool>, ::taihe::error> GetIsEnabled()
    {
        return optional<bool>::make(true);
    }
};

::taihe::expected<ShortcutInfo, ::taihe::error> GetShortcutInfo()
{
    return make_holder<ShortcutInfoImpl, ShortcutInfo>();
}
}  // namespace

TH_EXPORT_CPP_API_GetShortcutInfo(GetShortcutInfo);
// NOLINTEND
