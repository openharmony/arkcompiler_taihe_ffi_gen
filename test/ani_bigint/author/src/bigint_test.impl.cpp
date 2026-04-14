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
#include "bigint_test.impl.hpp"
#include <iostream>
#include "taihe/array.hpp"

using namespace taihe;

namespace {

::taihe::expected<bool, ::taihe::error> BigInt01(double a, ::taihe::array_view<int64_t> b)
{
    return true;
}

::taihe::expected<double, ::taihe::error> BigInt02(double a)
{
    return a;
}

::taihe::expected<::taihe::array<int64_t>, ::taihe::error> BigInt03(::taihe::array_view<int64_t> a)
{
    return a;
}

::taihe::expected<void, ::taihe::error> BigInt04(::taihe::array_view<int64_t> a)
{
    for (int i = 0; i < a.size(); i++) {
        std::cout << a[i] << std::endl;
    }
    return {};
}

::taihe::expected<::taihe::array<int64_t>, ::taihe::error> BigInt05(double a, ::taihe::array_view<int64_t> b)
{
    return b;
}

::taihe::expected<double, ::taihe::error> BigInt06(double a, ::taihe::array_view<int64_t> b)
{
    return a;
}
}  // namespace

TH_EXPORT_CPP_API_BigInt01(BigInt01);
TH_EXPORT_CPP_API_BigInt02(BigInt02);
TH_EXPORT_CPP_API_BigInt03(BigInt03);
TH_EXPORT_CPP_API_BigInt04(BigInt04);
TH_EXPORT_CPP_API_BigInt05(BigInt05);
TH_EXPORT_CPP_API_BigInt06(BigInt06);
// NOLINTEND