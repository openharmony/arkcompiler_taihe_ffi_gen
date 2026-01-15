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

#include "primitives_test.impl.hpp"

namespace {
// You can add using namespace statements here if needed.

::taihe::expected<int32_t, ::taihe::error> func1(int32_t a)
{
    return a + 1;
}

::taihe::expected<int64_t, ::taihe::error> func2(int64_t a)
{
    return a + 1;
}

::taihe::expected<uint32_t, ::taihe::error> func3(uint32_t a)
{
    return a + 1;
}

::taihe::expected<double, ::taihe::error> func4(double a)
{
    return a + 1;
}

::taihe::expected<bool, ::taihe::error> func5(bool a)
{
    return !a;
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
TH_EXPORT_CPP_API_func1(func1);
TH_EXPORT_CPP_API_func2(func2);
TH_EXPORT_CPP_API_func3(func3);
TH_EXPORT_CPP_API_func4(func4);
TH_EXPORT_CPP_API_func5(func5);
// NOLINTEND
