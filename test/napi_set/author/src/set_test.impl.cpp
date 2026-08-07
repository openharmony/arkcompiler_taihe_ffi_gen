/*
 * Copyright (c) 2026 Huawei Device Co., Ltd.
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

#include "set_test.impl.hpp"

namespace {
::taihe::expected<int32_t, ::taihe::error> getStringSetSize(::taihe::set_view<::taihe::string> values)
{
    return values.size();
}

::taihe::expected<::taihe::set<::taihe::string>, ::taihe::error> addString(::taihe::set_view<::taihe::string> values,
                                                                           ::taihe::string_view value)
{
    ::taihe::set<::taihe::string> result;
    for (auto const &item : values) {
        result.emplace(item);
    }
    result.emplace(value);
    return result;
}
}  // namespace

TH_EXPORT_CPP_API_getStringSetSize(getStringSetSize);
TH_EXPORT_CPP_API_addString(addString);
// NOLINTEND