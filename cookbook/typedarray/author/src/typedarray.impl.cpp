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
#include "typedarray.impl.hpp"
#include <iostream>
#include "stdexcept"
#include "taihe/runtime.hpp"
#include "typedarray.proj.hpp"

using namespace taihe;

namespace {
array<uint16_t> createUint16Array()
{
    return {1, 3, 5, 6, 9};
}

void printUint16Array(array_view<uint16_t> arr)
{
    size_t i = 0;
    for (uint16_t val : arr) {
        std::cout << "Index: " << i++ << " Value: " << val << std::endl;
    }
}
}  // namespace

TH_EXPORT_CPP_API_createUint16Array(createUint16Array);
TH_EXPORT_CPP_API_printUint16Array(printUint16Array);
// NOLINTEND
