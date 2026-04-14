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
#include "cb_compare.impl.hpp"
#include "cb_compare.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

namespace {
// To be implemented.

::taihe::expected<bool, ::taihe::error> cbCompare(
    ::taihe::callback_view<::taihe::expected<::taihe::string, ::taihe::error>()> cb1,
    ::taihe::callback_view<::taihe::expected<::taihe::string, ::taihe::error>()> cb2)
{
    return cb1 == cb2 ? true : false;
}

}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
TH_EXPORT_CPP_API_cbCompare(cbCompare);
// NOLINTEND
