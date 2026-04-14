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
#include "hello.impl.hpp"
#include <iostream>
#include "hello.proj.hpp"
#include "stdexcept"
#include "taihe/optional.hpp"
#include "taihe/runtime.hpp"

namespace {
// To be implemented.

::taihe::expected<void, ::taihe::error> setData(::hello::Data const &data)
{
    return {};
}

::taihe::expected<::hello::Data, ::taihe::error> getData()
{
    return ::hello::Data {
        .a = taihe::optional<taihe::string> {std::in_place, "name"},
        .b = taihe::optional<double> {std::in_place, 2.5},
        .c = taihe::optional<int> {std::in_place, 3},
        .d = taihe::optional<bool> {std::in_place, true},
        .e = taihe::optional<bool> {std::in_place, true},
        .f = taihe::optional<bool> {std::in_place, false},
        .g = taihe::optional<bool> {std::in_place, false},
    };
}

::taihe::expected<void, ::taihe::error> setRecord(::taihe::map_view<::taihe::string, ::taihe::string> rec)
{
    return {};
}

static ::taihe::map<::taihe::string, ::taihe::string> global_rec = [] {
    ::taihe::map<::taihe::string, ::taihe::string> rec;
    rec.emplace("key0", "value0");
    rec.emplace("key1", "value1");
    rec.emplace("key2", "value2");
    rec.emplace("key3", "value3");
    rec.emplace("key4", "value4");
    rec.emplace("key5", "value5");
    rec.emplace("key6", "value6");
    rec.emplace("key7", "value7");
    return rec;
}();

::taihe::expected<::taihe::map<::taihe::string, ::taihe::string>, ::taihe::error> getRecord()
{
    return global_rec;
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
TH_EXPORT_CPP_API_setData(setData);
TH_EXPORT_CPP_API_getData(getData);
TH_EXPORT_CPP_API_setRecord(setRecord);
TH_EXPORT_CPP_API_getRecord(getRecord);
// NOLINTEND
