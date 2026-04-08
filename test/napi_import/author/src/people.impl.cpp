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

#include "people.impl.hpp"
#include "people.proj.hpp"

namespace {
::taihe::expected<::people::student, ::taihe::error> make_student()
{
    return ::people::student {"mike", 22};
}
}  // namespace

TH_EXPORT_CPP_API_make_student(make_student);
// NOLINTEND
