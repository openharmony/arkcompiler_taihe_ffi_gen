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
#include <maythrow.impl.hpp>

#include <taihe/runtime.hpp>

namespace {
::taihe::expected<int32_t, ::taihe::error> maythrow_impl(int32_t a)
{
    if (a == 0) {
        return ::taihe::expected<int32_t, ::taihe::error>(::taihe::unexpect, "some error happen");
    } else {
        int const tempnum = 10;
        return a + tempnum;
    }
}

::taihe::expected<maythrow::Data, ::taihe::error> getDataMaythrow()
{
    return ::taihe::expected<maythrow::Data, ::taihe::error>(::taihe::unexpect, "error in getDataMaythrow");
}

::taihe::expected<void, ::taihe::error> noReturnMaythrow()
{
    return ::taihe::expected<void, ::taihe::error>(::taihe::unexpect, "error in noReturnMaythrow");
}

::taihe::expected<void, ::taihe::error> noReturnTypeError()
{
    return ::taihe::expected<void, ::taihe::error>(::taihe::unexpect, "noReturnTypeError");
}

::taihe::expected<void, ::taihe::error> noReturnRangeError()
{
    return ::taihe::expected<void, ::taihe::error>(::taihe::unexpect, "noReturnRangeError");
}
}  // namespace

// because these macros are auto-generate, lint will cause false positive.
TH_EXPORT_CPP_API_maythrow(maythrow_impl);
TH_EXPORT_CPP_API_getDataMaythrow(getDataMaythrow);
TH_EXPORT_CPP_API_noReturnMaythrow(noReturnMaythrow);
TH_EXPORT_CPP_API_noReturnTypeError(noReturnTypeError);
TH_EXPORT_CPP_API_noReturnRangeError(noReturnRangeError);
// NOLINTEND
