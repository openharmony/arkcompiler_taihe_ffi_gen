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

#include "array_test.impl.hpp"
#include <numeric>
#include "array_test.proj.hpp"
#include "taihe/object.hpp"

namespace {
::taihe::expected<int32_t, ::taihe::error> sumArray(::taihe::array_view<int32_t> nums, int32_t base)
{
    return std::accumulate(nums.begin(), nums.end(), base);
}

::taihe::expected<int64_t, ::taihe::error> getArrayValue(::taihe::array_view<int64_t> nums, int32_t idx)
{
    if (idx >= 0 && idx < nums.size()) {
        return nums[idx];
    }
    return 0;
}

::taihe::expected<::taihe::array<::taihe::string>, ::taihe::error> toStingArray(::taihe::array_view<int32_t> nums)
{
    auto result = ::taihe::array<::taihe::string>::make(nums.size(), "");
    std::transform(nums.begin(), nums.end(), result.begin(), [](int32_t n) {
        return ::taihe::to_string(n);
    });
    return result;
}

::taihe::expected<::taihe::array<int32_t>, ::taihe::error> makeIntArray(int32_t value, int32_t num)
{
    return ::taihe::array<int32_t>::make(num, value);
}

::taihe::expected<::taihe::array<::array_test::Color>, ::taihe::error> makeEnumArray(::array_test::Color value,
                                                                                     int32_t num)
{
    return ::taihe::array<::array_test::Color>::make(num, value);
}

::taihe::expected<::taihe::array<::array_test::Data>, ::taihe::error> makeStructArray(::taihe::string_view a,
                                                                                      ::taihe::string_view b, int32_t c,
                                                                                      int32_t num)
{
    return ::taihe::array<::array_test::Data>::make(num, ::array_test::Data {a, b, c});
}

::taihe::expected<::taihe::array<::array_test::Color>, ::taihe::error> changeEnumArray(
    ::taihe::array_view<::array_test::Color> value, ::array_test::Color color)
{
    auto result = ::taihe::array<::array_test::Color>::make(value.size(), value[0]);
    std::transform(value.begin(), value.end(), result.begin(), [color](::array_test::Color c) {
        return color;
    });
    return result;
}

::taihe::expected<::taihe::array<::array_test::Data>, ::taihe::error> changeStructArray(
    ::taihe::array_view<::array_test::Data> value, ::taihe::string_view a, ::taihe::string_view b, int32_t c)
{
    auto result = ::taihe::array<::array_test::Data>::make(value.size(), value[0]);
    std::transform(value.begin(), value.end(), result.begin(), [a, b, c](::array_test::Data d) {
        return ::array_test::Data {a, b, c};
    });
    return result;
}

::taihe::expected<::taihe::array<::taihe::array<::array_test::Data>>, ::taihe::error> makeStructArrayArray(
    ::taihe::string_view a, ::taihe::string_view b, int32_t c, int32_t num1, int32_t num2)
{
    auto arr = ::taihe::array<::array_test::Data>::make(num1, ::array_test::Data {a, b, c});
    return ::taihe::array<::taihe::array<::array_test::Data>>::make(num2, arr);
}

class Base {
protected:
    ::taihe::string id;

public:
    Base(::taihe::string_view id) : id(id)
    {
        std::cout << "new base " << this << std::endl;
    }

    ~Base()
    {
        std::cout << "del shape " << this << std::endl;
    }

    ::taihe::expected<::taihe::string, ::taihe::error> getId()
    {
        return id;
    }

    ::taihe::expected<void, ::taihe::error> setId(::taihe::string_view s)
    {
        id = s;
        return {};
    }
};

::taihe::expected<::taihe::array<::array_test::IBase>, ::taihe::error> makeIfaceArray(::taihe::string_view a)
{
    auto base = ::taihe::make_holder<Base, ::array_test::IBase>(a);
    return ::taihe::array<::array_test::IBase>::make(1, base);
}

::taihe::expected<::taihe::array<::array_test::IBase>, ::taihe::error> changeIfaceArray(
    ::taihe::array_view<::array_test::IBase> value, ::taihe::string_view a)
{
    ::taihe::array<::array_test::IBase> res = value;
    for (int i = 0; i < value.size(); i++) {
        res[i]->setId(a);
    }
    return res;
}
}  // namespace

TH_EXPORT_CPP_API_sumArray(sumArray);
TH_EXPORT_CPP_API_getArrayValue(getArrayValue);
TH_EXPORT_CPP_API_toStingArray(toStingArray);
TH_EXPORT_CPP_API_makeIntArray(makeIntArray);
TH_EXPORT_CPP_API_makeEnumArray(makeEnumArray);
TH_EXPORT_CPP_API_changeEnumArray(changeEnumArray);
TH_EXPORT_CPP_API_makeStructArray(makeStructArray);
TH_EXPORT_CPP_API_changeStructArray(changeStructArray);
TH_EXPORT_CPP_API_makeStructArrayArray(makeStructArrayArray);
TH_EXPORT_CPP_API_makeIfaceArray(makeIfaceArray);
TH_EXPORT_CPP_API_changeIfaceArray(changeIfaceArray);
// NOLINTEND
