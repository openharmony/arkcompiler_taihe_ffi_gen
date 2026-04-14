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
#include <cstdint>
#include <iostream>

#include "enum_test.impl.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"
#include "taihe/string.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {
static constexpr std::size_t COLOR_COUNT = 3;
static constexpr std::size_t WEEKDAY_COUNT = 7;
static constexpr std::size_t NUMTYPEI8_COUNT = 3;
static constexpr std::size_t NUMTYPEI16_COUNT = 3;
static constexpr std::size_t NUMTYPEI32_COUNT = 3;
static constexpr std::size_t NUMTYPEI64_COUNT = 3;
static constexpr std::size_t BOOL_COUNT = 3;

::taihe::expected<::enum_test::Color, ::taihe::error> NextEnum(::enum_test::Color color)
{
    return (::enum_test::Color::key_t)(((int)color.get_key() + 1) % COLOR_COUNT);
}

::taihe::expected<::taihe::string, ::taihe::error> GetValueOfEnum(::enum_test::Color color)
{
    return color.get_value();
}

::taihe::expected<::enum_test::Color, ::taihe::error> fromValueToEnum(string_view name)
{
    auto color = ::enum_test::Color::from_value(name);
    if (!color.is_valid()) {
        return ::taihe::unexpected<::taihe::error>(::taihe::error("Invalid enum value", 1));
    }
    return color;
}

::taihe::expected<::enum_test::Weekday, ::taihe::error> NextEnumWeekday(::enum_test::Weekday day)
{
    return (::enum_test::Weekday::key_t)(((int)day.get_key() + 1) % WEEKDAY_COUNT);
}

::taihe::expected<int32_t, ::taihe::error> GetValueOfEnumWeekday(::enum_test::Weekday day)
{
    return day.get_value();
}

::taihe::expected<::enum_test::Weekday, ::taihe::error> fromValueToEnumWeekday(int day)
{
    auto weekday = ::enum_test::Weekday::from_value(day);
    if (!weekday.is_valid()) {
        return ::taihe::unexpected<::taihe::error>(::taihe::error("Invalid enum value", 1));
    }
    return weekday;
}

::taihe::expected<::enum_test::NumTypeI8, ::taihe::error> NextEnumI8(::enum_test::NumTypeI8 numTypei8)
{
    return (::enum_test::NumTypeI8::key_t)(((int)numTypei8.get_key() + 1) % NUMTYPEI8_COUNT);
}

::taihe::expected<::enum_test::NumTypeI16, ::taihe::error> NextEnumI16(::enum_test::NumTypeI16 numTypeI16)
{
    return (::enum_test::NumTypeI16::key_t)(((int)numTypeI16.get_key() + 1) % NUMTYPEI16_COUNT);
}

::taihe::expected<::enum_test::NumTypeI32, ::taihe::error> NextEnumI32(::enum_test::NumTypeI32 numTypeI32)
{
    return (::enum_test::NumTypeI32::key_t)(((int)numTypeI32.get_key() + 1) % NUMTYPEI32_COUNT);
}

::taihe::expected<::enum_test::NumTypeI64, ::taihe::error> NextEnumI64(::enum_test::NumTypeI64 numTypeI64)
{
    return (::enum_test::NumTypeI64::key_t)(((int)numTypeI64.get_key() + 1) % NUMTYPEI64_COUNT);
}

::taihe::expected<::enum_test::EnumString, ::taihe::error> NextEnumString(::enum_test::EnumString enumString)
{
    return (::enum_test::EnumString::key_t)(((int)enumString.get_key() + 1) % BOOL_COUNT);
}

}  // namespace

TH_EXPORT_CPP_API_nextEnum(NextEnum);
TH_EXPORT_CPP_API_getValueOfEnum(GetValueOfEnum);
TH_EXPORT_CPP_API_fromValueToEnum(fromValueToEnum);
TH_EXPORT_CPP_API_nextEnumWeekday(NextEnumWeekday);
TH_EXPORT_CPP_API_getValueOfEnumWeekday(GetValueOfEnumWeekday);
TH_EXPORT_CPP_API_fromValueToEnumWeekday(fromValueToEnumWeekday);
TH_EXPORT_CPP_API_nextEnumI8(NextEnumI8);
TH_EXPORT_CPP_API_nextEnumI16(NextEnumI16);
TH_EXPORT_CPP_API_nextEnumI32(NextEnumI32);
TH_EXPORT_CPP_API_nextEnumI64(NextEnumI64);
TH_EXPORT_CPP_API_nextEnumString(NextEnumString);
// NOLINTEND
