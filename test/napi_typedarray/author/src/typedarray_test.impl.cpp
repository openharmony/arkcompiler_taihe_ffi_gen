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

#include "typedarray_test.impl.hpp"
#include <iostream>
#include <numeric>
#include "typedarray_test.proj.hpp"

namespace {

::taihe::expected<int8_t, ::taihe::error> SumUint8Array(::taihe::array_view<uint8_t> v)
{
    return std::accumulate(v.begin(), v.end(), 0);
}

::taihe::expected<::taihe::array<uint8_t>, ::taihe::error> NewUint8Array(int64_t n, int8_t v)
{
    ::taihe::array<uint8_t> result(n);
    std::fill(result.begin(), result.end(), v);
    return result;
}

::taihe::expected<float, ::taihe::error> SumFloat32Array(::taihe::array_view<float> v)
{
    return std::accumulate(v.begin(), v.end(), 0.0f);
}

::taihe::expected<::taihe::array<float>, ::taihe::error> NewFloat32Array(int64_t n, float v)
{
    ::taihe::array<float> result(n);
    std::fill(result.begin(), result.end(), v);
    return result;
}
}  // namespace

TH_EXPORT_CPP_API_SumUint8Array(SumUint8Array);
TH_EXPORT_CPP_API_NewUint8Array(NewUint8Array);
TH_EXPORT_CPP_API_SumFloat32Array(SumFloat32Array);
TH_EXPORT_CPP_API_NewFloat32Array(NewFloat32Array);
// NOLINTEND
