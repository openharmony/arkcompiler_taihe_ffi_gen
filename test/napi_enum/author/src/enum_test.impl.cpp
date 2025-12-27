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

#include "enum_test.impl.hpp"
#include "enum_test.proj.hpp"

namespace {
static constexpr std::size_t COLOR_COUNT = 3;
static constexpr std::size_t WEEKDAY_COUNT = 7;
static constexpr std::size_t NUMTYPEI8_COUNT = 3;
static constexpr std::size_t NUMTYPEI16_COUNT = 3;
static constexpr std::size_t NUMTYPEI32_COUNT = 3;
static constexpr std::size_t NUMTYPEI64_COUNT = 3;
static constexpr std::size_t BOOL_COUNT = 3;

::taihe::expected<::enum_test::Color, ::taihe::error> nextEnum(::enum_test::Color color)
{
    return (::enum_test::Color::key_t)(((int)color.get_key() + 1) % COLOR_COUNT);
}

::taihe::expected<taihe::string, ::taihe::error> getValueOfEnum(::enum_test::Color color)
{
    return color.get_value();
}

::taihe::expected<::enum_test::Color, ::taihe::error> fromValueToEnum(::taihe::string_view name)
{
    auto color = ::enum_test::Color::from_value(name);
    return color;
}

::taihe::expected<::enum_test::Weekday, ::taihe::error> nextEnumWeekday(::enum_test::Weekday day)
{
    return (::enum_test::Weekday::key_t)(((int)day.get_key() + 1) % WEEKDAY_COUNT);
}

::taihe::expected<int32_t, ::taihe::error> getValueOfEnumWeekday(::enum_test::Weekday day)
{
    return day.get_value();
}

::taihe::expected<::enum_test::Weekday, ::taihe::error> fromValueToEnumWeekday(int day)
{
    auto weekday = ::enum_test::Weekday::from_value(day);
    return weekday;
}
}  // namespace

TH_EXPORT_CPP_API_nextEnum(nextEnum);
TH_EXPORT_CPP_API_getValueOfEnum(getValueOfEnum);
TH_EXPORT_CPP_API_fromValueToEnum(fromValueToEnum);
TH_EXPORT_CPP_API_nextEnumWeekday(nextEnumWeekday);
TH_EXPORT_CPP_API_getValueOfEnumWeekday(getValueOfEnumWeekday);
TH_EXPORT_CPP_API_fromValueToEnumWeekday(fromValueToEnumWeekday);
// NOLINTEND
