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

#include "arraybuffer_test.impl.hpp"
#include <numeric>
#include "arraybuffer_test.proj.hpp"

namespace {
::taihe::expected<uint8_t, ::taihe::error> SumArrayU8(::taihe::array_view<uint8_t> nums)
{
    return std::accumulate(nums.begin(), nums.end(), 0);
}

::taihe::expected<::taihe::array<uint8_t>, ::taihe::error> GetArrayBuffer(uint8_t nums)
{
    ::taihe::array<uint8_t> result = ::taihe::array<uint8_t>::make(nums);
    std::fill(result.begin(), result.end(), nums);
    return result;
}
}  // namespace

TH_EXPORT_CPP_API_SumArrayU8(SumArrayU8);
TH_EXPORT_CPP_API_GetArrayBuffer(GetArrayBuffer);
// NOLINTEND
