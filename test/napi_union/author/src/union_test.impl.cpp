/*
 * Copyright (c) 2025-2026 Huawei Device Co., Ltd.
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
::taihe::expected<::taihe::string, ::taihe::error> printUnion(::union_test::union_primitive const &data)
{
    switch (data.get_tag()) {
        case ::union_test::union_primitive::tag_t::stringValue:
            std::cout << "string: " << data.get_stringValue_ref() << std::endl;
            return "string";
        case ::union_test::union_primitive::tag_t::numberValue:
            std::cout << "number: " << (int)data.get_numberValue_ref() << std::endl;
            return "number";
        case ::union_test::union_primitive::tag_t::booleanValue:
            std::cout << "boolean: " << data.get_booleanValue_ref() << std::endl;
            return "boolean";
        case ::union_test::union_primitive::tag_t::arrayValue:
            std::cout << "array: " << data.get_arrayValue_ref()[0] << std::endl;
            return "array";
        case ::union_test::union_primitive::tag_t::mapValue:
            std::cout << "map: " << std::endl;
            for (auto const &[key, val] : data.get_mapValue_ref()) {
                std::cout << "C++ Map: key: " << key << " value: " << val << std::endl;
            }
            return "map";
        case ::union_test::union_primitive::tag_t::setValue:
            std::cout << "set: " << std::endl;
            for (auto const &val : data.get_setValue_ref()) {
                std::cout << "C++ Set: value: " << val << std::endl;
            }
            return "set";
        case ::union_test::union_primitive::tag_t::int16arrayValue:
            std::cout << "int16array: " << std::endl;
            for (auto const &val : data.get_int16arrayValue_ref()) {
                std::cout << "C++ Int16Array: value: " << val << std::endl;
            }
            return "int16array";
        case ::union_test::union_primitive::tag_t::int32arrayValue:
            std::cout << "int32array: " << std::endl;
            for (auto const &val : data.get_int32arrayValue_ref()) {
                std::cout << "C++ Int32Array: value: " << val << std::endl;
            }
            return "int32array";
        case ::union_test::union_primitive::tag_t::arraybufferValue:
            std::cout << "arraybuffer: " << std::endl;
            for (auto const &val : data.get_arraybufferValue_ref()) {
                std::cout << "C++ ArrayBuffer: value: " << static_cast<int>(val) << std::endl;
            }
            return "arraybuffer";
        case ::union_test::union_primitive::tag_t::bigintValue:
            std::cout << "bigint: " << std::endl;
            for (auto const &val : data.get_bigintValue_ref()) {
                std::cout << "C++ BigInt: value: " << val << std::endl;
            }
            return "bigint";
        case ::union_test::union_primitive::tag_t::fooValue:
            std::cout << "foo: " << std::endl;
            std::cout << "C++ Foo: a: " << data.get_fooValue_ref().a << " b: " << data.get_fooValue_ref().b
                      << std::endl;
            return "foo";
        case ::union_test::union_primitive::tag_t::barValue:
            std::cout << "bar: " << std::endl;
            return "bar";
        case ::union_test::union_primitive::tag_t::undefinedValue:
            return "undefined";
        case ::union_test::union_primitive::tag_t::nullValue:
            return "null";
    }
}

::taihe::expected<::union_test::union_primitive, ::taihe::error> makeUnion(::taihe::string_view kind)
{
    ::taihe::string str_value = "string";
    constexpr double f64_value = 1.12345;
    constexpr bool bool_value = false;
    constexpr int32_t i32_value1 = 1;
    constexpr int32_t i32_value2 = 2;
    ::taihe::array<int32_t> array_value = ::taihe::array<int32_t> {1, 2, 3};
    ::taihe::map<int32_t, ::taihe::string> map_value;
    map_value.emplace(i32_value1, "a");
    map_value.emplace(i32_value2, "b");
    ::taihe::set<::taihe::string> set_value;
    set_value.emplace("a");
    set_value.emplace("b");
    ::taihe::array<int16_t> int16array_value = ::taihe::array<int16_t> {1, 2, 3};
    ::taihe::array<int32_t> int32array_value = ::taihe::array<int32_t> {1, 2, 3};
    ::taihe::array<uint8_t> arraybuffer_value = ::taihe::array<uint8_t> {1, 2, 3};
    ::taihe::array<uint64_t> bigint_value = ::taihe::array<uint64_t> {1, 2, 3};

    if (kind == "string") {
        return ::union_test::union_primitive::make_stringValue(str_value);
    }
    if (kind == "number") {
        return ::union_test::union_primitive::make_numberValue(f64_value);
    }
    if (kind == "boolean") {
        return ::union_test::union_primitive::make_booleanValue(bool_value);
    }
    if (kind == "array") {
        return ::union_test::union_primitive::make_arrayValue(array_value);
    }
    if (kind == "map") {
        return ::union_test::union_primitive::make_mapValue(map_value);
    }
    if (kind == "set") {
        return ::union_test::union_primitive::make_setValue(set_value);
    }
    if (kind == "int16array") {
        return ::union_test::union_primitive::make_int16arrayValue(int16array_value);
    }
    if (kind == "int32array") {
        return ::union_test::union_primitive::make_int32arrayValue(int32array_value);
    }
    if (kind == "arraybuffer") {
        return ::union_test::union_primitive::make_arraybufferValue(arraybuffer_value);
    }
    if (kind == "bigint") {
        return ::union_test::union_primitive::make_bigintValue(bigint_value);
    }
    if (kind == "null") {
        return ::union_test::union_primitive::make_nullValue();
    }
    return ::union_test::union_primitive::make_undefinedValue();
}

::taihe::expected<::union_test::Foo, ::taihe::error> makeFoo(int a, ::taihe::string_view b)
{
    return ::union_test::Foo {a, b};
}

::taihe::expected<::union_test::Bar, ::taihe::error> makeBar()
{
    return taihe::make_holder<std::tuple<>, ::union_test::Bar>();
}
}  // namespace

TH_EXPORT_CPP_API_printUnion(printUnion);
TH_EXPORT_CPP_API_makeUnion(makeUnion);
TH_EXPORT_CPP_API_makeFoo(makeFoo);
TH_EXPORT_CPP_API_makeBar(makeBar);
// NOLINTEND
