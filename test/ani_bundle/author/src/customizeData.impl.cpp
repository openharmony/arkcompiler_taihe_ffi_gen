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
#include "customizeData.impl.hpp"
#include <iostream>
#include "customizeData.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace customizeData;

namespace {

class CustomizeDataImpl {
public:
    string name_ = "bob";
    string value_ = "jack";
    string extra_ = "john";

    CustomizeDataImpl()
    {
    }

    ::taihe::expected<void, ::taihe::error> SetName(string_view name)
    {
        name_ = name;
        return {};
    }

    ::taihe::expected<string, ::taihe::error> GetName()
    {
        return name_;
    }

    ::taihe::expected<void, ::taihe::error> SetValue(string_view value)
    {
        value_ = value;
        return {};
    }

    ::taihe::expected<string, ::taihe::error> GetValue()
    {
        return value_;
    }

    ::taihe::expected<void, ::taihe::error> SetExtra(string_view extra)
    {
        extra_ = extra;
        return {};
    }

    ::taihe::expected<string, ::taihe::error> GetExtra()
    {
        return extra_;
    }
};

::taihe::expected<CustomizeData, ::taihe::error> GetCustomizeData()
{
    return make_holder<CustomizeDataImpl, CustomizeData>();
}
}  // namespace

TH_EXPORT_CPP_API_GetCustomizeData(GetCustomizeData);
// NOLINTEND
