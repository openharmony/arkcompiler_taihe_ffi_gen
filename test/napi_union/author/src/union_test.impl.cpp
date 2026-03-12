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

#include "union_test.impl.hpp"
#include "union_test.proj.hpp"

namespace {
::taihe::string printUnion(::union_test::union_primitive const &data)
{
    switch (data.get_tag()) {
        case ::union_test::union_primitive::tag_t::sValue:
            std::cout << "s: " << data.get_sValue_ref() << std::endl;
            return "s";
        case ::union_test::union_primitive::tag_t::numberValue:
            std::cout << "number: " << (int)data.get_numberValue_ref() << std::endl;
            return "number";
        case ::union_test::union_primitive::tag_t::bValue:
            std::cout << "bool: " << data.get_bValue_ref() << std::endl;
            return "bool";
        case ::union_test::union_primitive::tag_t::aValue:
            std::cout << "array: " << data.get_aValue_ref()[0] << std::endl;
            return "array";
        case ::union_test::union_primitive::tag_t::mValue:
            std::cout << "map: " << std::endl;
            for (auto const &[key, val] : data.get_mValue_ref()) {
                std::cout << "C++ Map: key: " << key << " value: " << val << std::endl;
            }
            return "map";
        case ::union_test::union_primitive::tag_t::uValue:
            return "undefined";
        case ::union_test::union_primitive::tag_t::nValue:
            return "null";
    }
}

::union_test::union_primitive makeUnion(::taihe::string_view kind)
{
    ::taihe::string s_value = "string";
    constexpr double f64_value = 1.12345;
    constexpr bool bool_value = false;
    constexpr int32_t i32_value1 = 1;
    constexpr int32_t i32_value2 = 2;
    ::taihe::array<int32_t> array_value = ::taihe::array<int32_t> {1, 2, 3};
    ::taihe::map<int32_t, ::taihe::string> map_value;
    map_value.emplace(i32_value1, "a");
    map_value.emplace(i32_value2, "b");

    if (kind == "s") {
        return ::union_test::union_primitive::make_sValue(s_value);
    }
    if (kind == "number") {
        return ::union_test::union_primitive::make_numberValue(f64_value);
    }
    if (kind == "bool") {
        return ::union_test::union_primitive::make_bValue(bool_value);
    }
    if (kind == "array") {
        return ::union_test::union_primitive::make_aValue(array_value);
    }
    if (kind == "map") {
        return ::union_test::union_primitive::make_mValue(map_value);
    }
    if (kind == "undefined") {
        return ::union_test::union_primitive::make_uValue();
    }
    if (kind == "null") {
        return ::union_test::union_primitive::make_nValue();
    }
    return ::union_test::union_primitive::make_uValue();
}
}  // namespace

TH_EXPORT_CPP_API_printUnion(printUnion);
TH_EXPORT_CPP_API_makeUnion(makeUnion);
// NOLINTEND
