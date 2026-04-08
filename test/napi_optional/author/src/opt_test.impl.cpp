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

#include "opt_test.impl.hpp"
#include <iostream>
#include "opt_test.proj.hpp"

namespace {
::taihe::expected<void, ::taihe::error> showOptionalInt(::taihe::optional_view<int32_t> x)
{
    if (x) {
        std::cout << *x << std::endl;
    } else {
        std::cout << "Null" << std::endl;
    }
    return {};
}

::taihe::expected<::taihe::optional<int32_t>, ::taihe::error> makeOptionalInt(bool b)
{
    if (b) {
        int const optionalMakeValue = 10;
        return ::taihe::optional<int32_t>::make(optionalMakeValue);
    } else {
        return ::taihe::optional<int32_t>(nullptr);
    }
}

}  // namespace

TH_EXPORT_CPP_API_showOptionalInt(showOptionalInt);
TH_EXPORT_CPP_API_makeOptionalInt(makeOptionalInt);
// NOLINTEND
