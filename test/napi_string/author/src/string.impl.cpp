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

#include "string_test.impl.hpp"

namespace {

taihe::string ohos_concat_str(taihe::string_view a, taihe::string_view b)
{
    return a + b;
}

taihe::string ohos_int_to_str(int32_t n)
{
    return taihe::to_string(n);
}

int32_t ohos_str_to_int(taihe::string_view pstr)
{
    return std::atoi(pstr.c_str());
}

taihe::string ohos_show()
{
    return "success";
}

int32_t add(int32_t a, int32_t b)
{
    return a + b;
}

uint64_t sum(uint64_t a, uint64_t b)
{
    return (a * b);
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_concat(ohos_concat_str);
TH_EXPORT_CPP_API_to_i32(ohos_str_to_int);
TH_EXPORT_CPP_API_from_i32(ohos_int_to_str);
TH_EXPORT_CPP_API_show(ohos_show);
TH_EXPORT_CPP_API_add(add);
TH_EXPORT_CPP_API_sum(sum);
// NOLINTEND
