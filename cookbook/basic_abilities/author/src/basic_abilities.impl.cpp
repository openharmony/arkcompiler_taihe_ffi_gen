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
#include "basic_abilities.impl.hpp"

#include "stdexcept"
#include "taihe/array.hpp"
#include "taihe/string.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {

::taihe::expected<::taihe::array<::taihe::string>, ::taihe::error> convert_arr(::taihe::array_view<int32_t> a,
                                                                               ::taihe::string_view str)
{
    int32_t input_size = a.size();
    int32_t input_begin_val = a[0];
    int32_t input_end_val = a[input_size - 1];
    ::taihe::array<::taihe::string> res = {
        {std::to_string(input_size)}, {std::to_string(input_begin_val)}, {std::to_string(input_end_val)}, str};
    return res;
}

}  // namespace

TH_EXPORT_CPP_API_convert_arr(convert_arr);
// NOLINTEND
