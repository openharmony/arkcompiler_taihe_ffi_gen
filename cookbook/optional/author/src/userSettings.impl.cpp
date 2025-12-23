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

#include "userSettings.impl.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"
#include "userSettings.proj.hpp"

using namespace taihe;

namespace {
optional<string> getUserSetting(map_view<string, string> settings, string_view key)
{
    auto iter = settings.find_item(key);
    if (iter == nullptr) {
        return optional<string>(std::nullopt);
    }
    return optional<string>(std::in_place, iter->second);
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_getUserSetting(getUserSetting);
// NOLINTEND
