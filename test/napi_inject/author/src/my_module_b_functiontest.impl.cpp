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

#include "my_module_b.functiontest.impl.hpp"
#include "my_module_b.functiontest.proj.hpp"

namespace {
::taihe::string concat_str(::taihe::string_view a)
{
    return a + "_concat";
}

int32_t concat_i32(int32_t a)
{
    constexpr int32_t OFFSET = 10;
    return a + OFFSET;
}

}  // namespace

TH_EXPORT_CPP_API_concat_str(concat_str);
TH_EXPORT_CPP_API_concat_i32(concat_i32);
// NOLINTEND
