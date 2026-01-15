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

#include "record_test.impl.hpp"
#include "record_test.proj.hpp"

namespace {
::taihe::expected<int32_t, ::taihe::error> getStringIntSize(::taihe::map_view<::taihe::string, int32_t> r)
{
    return r.size();
}

::taihe::expected<::taihe::map<::taihe::string, ::taihe::string>, ::taihe::error> createStringString(int32_t a)
{
    ::taihe::map<::taihe::string, ::taihe::string> m;
    while (a--) {
        m.emplace(::taihe::to_string(a), "abc");
    }
    return m;
}

::taihe::expected<::taihe::map<::taihe::string, ::taihe::map<::taihe::string, int32_t>>, ::taihe::error> changeRecRec(
    ::taihe::map_view<::taihe::string, ::taihe::map<::taihe::string, int32_t>> a)
{
    ::taihe::map<::taihe::string, ::taihe::map<::taihe::string, int32_t>> result;
    for (auto const &[outer_key, inner_map] : a) {
        ::taihe::map<::taihe::string, int32_t> new_inner_map;
        for (auto const &[inner_key, value] : inner_map) {
            new_inner_map.emplace(inner_key, value * 2);
        }
        result.emplace(outer_key, std::move(new_inner_map));
    }
    return result;
}

::taihe::expected<void, ::taihe::error> setStringColor(::taihe::map_view<::taihe::string, ::record_test::Color> m)
{
    for (auto const &[key, val] : m) {
        std::cout << "C++ MapStringColor: key: " << key << " value: " << val << std::endl;
    }
    return {};
}

::taihe::expected<::taihe::map<::taihe::string, ::record_test::Color>, ::taihe::error> getStringColor()
{
    ::taihe::map<::taihe::string, ::record_test::Color> result;
    result.emplace("key1", record_test::Color::key_t::RED);
    result.emplace("key2", record_test::Color::key_t::GREEN);
    return result;
}

::taihe::expected<void, ::taihe::error> setStringData(::taihe::map_view<::taihe::string, ::record_test::Data> m)
{
    for (auto const &[key, val] : m) {
        std::cout << "C++ MapStringColor: key: " << key << " value: ";
        std::cout << val.a << " " << val.b << " " << val.c << std::endl;
    }
    return {};
}

::taihe::expected<::taihe::map<::taihe::string, ::record_test::Data>, ::taihe::error> getStringData()
{
    ::taihe::map<::taihe::string, ::record_test::Data> result;
    result.emplace("key1", ::record_test::Data {"a1", "b1", 1});
    result.emplace("key2", ::record_test::Data {"a2", "b2", 2});
    return result;
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

::taihe::expected<void, ::taihe::error> setStringIBase(::taihe::map_view<::taihe::string, ::record_test::IBase> m)
{
    for (auto const &[key, val] : m) {
        ::taihe::expected<::taihe::string, ::taihe::error> res = val->getId();
        if (res.has_value()) {
            std::cout << "C++ MapStringIBase: key: " << key << " value: " << res.value() << std::endl;
        }
    }
    return {};
}

::taihe::expected<::taihe::map<::taihe::string, ::record_test::IBase>, ::taihe::error> getStringIBase()
{
    auto basea = ::taihe::make_holder<Base, ::record_test::IBase>("basea");
    auto baseb = ::taihe::make_holder<Base, ::record_test::IBase>("baseb");
    ::taihe::map<::taihe::string, ::record_test::IBase> result;
    result.emplace("key1", basea);
    result.emplace("key2", baseb);
    return result;
}

}  // namespace

TH_EXPORT_CPP_API_getStringIntSize(getStringIntSize);
TH_EXPORT_CPP_API_createStringString(createStringString);
TH_EXPORT_CPP_API_changeRecRec(changeRecRec);
TH_EXPORT_CPP_API_setStringColor(setStringColor);
TH_EXPORT_CPP_API_getStringColor(getStringColor);
TH_EXPORT_CPP_API_setStringData(setStringData);
TH_EXPORT_CPP_API_getStringData(getStringData);
TH_EXPORT_CPP_API_setStringIBase(setStringIBase);
TH_EXPORT_CPP_API_getStringIBase(getStringIBase);
// NOLINTEND
