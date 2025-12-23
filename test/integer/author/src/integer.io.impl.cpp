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

#include "integer.io.impl.hpp"

#include <iostream>

int32_t ohos_int_input()
{
    int n;
    std::cin >> n;
    return n;
}

void ohos_int_output(int32_t n)
{
    std::cout << n << std::endl;
}

// NOLINTBEGIN
TH_EXPORT_CPP_API_input_i32(ohos_int_input);
TH_EXPORT_CPP_API_output_i32(ohos_int_output);
// NOLINTEND
