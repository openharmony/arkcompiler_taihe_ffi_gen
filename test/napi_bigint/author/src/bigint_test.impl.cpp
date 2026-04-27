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

#include <iostream>
#include "bigint_test.impl.hpp"
#include "bigint_test.proj.hpp"

namespace {

::taihe::expected<::taihe::array<uint64_t>, ::taihe::error> processBigInt(::taihe::array_view<uint64_t> a)
{
    ::taihe::array<uint64_t> res(a.size() + 1);
    res[0] = 0;
    for (int i = 0; i < a.size(); i++) {
        res[i + 1] = a[i];
        std::cout << "arr[" << i << "] = " << a[i] << std::endl;
    }
    return res;
}
}  // namespace

TH_EXPORT_CPP_API_processBigInt(processBigInt);
// NOLINTEND
