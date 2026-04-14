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
#include "optional.impl.hpp"
#include "optional.ExampleInterface.proj.2.hpp"
#include "optional.Union.proj.1.hpp"
#include "taihe/map.hpp"
#include "taihe/optional.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {
class ExampleInterface {
public:
    ::taihe::expected<void, ::taihe::error> FuncPrimitiveI8(optional_view<int8_t> param1)
    {
        std::cout << "opt1 has value: " << *param1 << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> FuncPrimitiveI16(optional_view<int16_t> param1)
    {
        std::cout << "opt1 has value: " << *param1 << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> FuncPrimitiveI32(optional_view<int32_t> param1)
    {
        std::cout << "opt1 has value: " << *param1 << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> FuncPrimitiveI64(optional_view<int64_t> param1)
    {
        std::cout << "opt1 has value: " << *param1 << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> FuncPrimitiveF32(optional_view<float> param1)
    {
        std::cout << "opt1 has value: " << *param1 << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> FuncPrimitiveF64(optional_view<double> param1)
    {
        std::cout << "opt1 has value: " << *param1 << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> FuncPrimitiveBool(optional_view<bool> param1)
    {
        std::cout << "opt1 has value: " << *param1 << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> FuncPrimitiveString(optional_view<string> param1)
    {
        std::cout << "opt1 has value: " << *param1 << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> FuncArray(optional_view<array<int32_t>> param1)
    {
        std::cout << "func_Array: [";
        for (auto const &elem : *param1) {
            std::cout << elem << " ";
        }
        std::cout << "]" << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> FuncBuffer(optional_view<array<uint8_t>> param1)
    {
        std::cout << "func_Array: [";
        for (auto const &elem : *param1) {
            std::cout << (int)elem << " ";
        }
        std::cout << "]" << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> FuncUnion(optional_view<::optional::Union> param1)
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> FuncMap(optional_view<map<string, int32_t>> param1)
    {
        for (auto it = (*param1).begin(); it != (*param1).end(); ++it) {
            auto const &[key, value] = *it;
            std::cout << "Key: " << key << ", Value: " << value << std::endl;
        }
        return {};
    }

    ::taihe::expected<::taihe::optional<string>, ::taihe::error> GetName()
    {
        return ::taihe::optional<string>::make("hello");
    }

    ::taihe::expected<::taihe::optional<int8_t>, ::taihe::error> Geti8()
    {
        int8_t const geti8Value = 1;
        return ::taihe::optional<int8_t>::make(geti8Value);
    }

    ::taihe::expected<::taihe::optional<int16_t>, ::taihe::error> Geti16()
    {
        int16_t const geti16Value = 100;
        return ::taihe::optional<int16_t>::make(geti16Value);
    }

    ::taihe::expected<::taihe::optional<int32_t>, ::taihe::error> Geti32()
    {
        int32_t const geti32Value = 1024;
        return ::taihe::optional<int32_t>::make(geti32Value);  // 默认返回 0
    }

    ::taihe::expected<::taihe::optional<int64_t>, ::taihe::error> Geti64()
    {
        int64_t const geti64Value = 999999;
        return ::taihe::optional<int64_t>::make(geti64Value);  // 默认返回 0
    }

    ::taihe::expected<::taihe::optional<float>, ::taihe::error> Getf32()
    {
        float const getf32Value = 0.0f;
        return ::taihe::optional<float>::make(getf32Value);
    }

    ::taihe::expected<::taihe::optional<double>, ::taihe::error> Getf64()
    {
        double const getf64Value = 0.0;
        return ::taihe::optional<double>::make(getf64Value);
    }

    ::taihe::expected<::taihe::optional<bool>, ::taihe::error> Getbool()
    {
        return ::taihe::optional<bool>::make(false);
    }

    ::taihe::expected<::taihe::optional<array<uint8_t>>, ::taihe::error> GetArraybuffer()
    {
        int const arrSize = 10;
        int const arrNum = 6;
        return ::taihe::optional<array<uint8_t>>::make(array<uint8_t>::make(arrSize, arrNum));
    }
};

::taihe::expected<::optional::ExampleInterface, ::taihe::error> GetInterface()
{
    return make_holder<ExampleInterface, ::optional::ExampleInterface>();
}

::taihe::expected<void, ::taihe::error> PrintTestInterfaceName(::optional::weak::ExampleInterface testiface)
{
    auto res = testiface->GetName();
    if (res.has_value() && res.value().has_value()) {
        std::cout << __func__ << ": " << res.value().value() << std::endl;
    }
    return {};
}

::taihe::expected<void, ::taihe::error> PrintTestInterfaceNumberi8(::optional::weak::ExampleInterface testiface)
{
    auto res = testiface->Geti8();
    if (res.has_value() && res.value().has_value()) {
        std::cout << __func__ << ": " << res.value().value() << std::endl;
    }
    return {};
}

::taihe::expected<void, ::taihe::error> PrintTestInterfaceNumberi16(::optional::weak::ExampleInterface testiface)
{
    auto res = testiface->Geti16();
    if (res.has_value() && res.value().has_value()) {
        std::cout << __func__ << ": " << res.value().value() << std::endl;
    }
    return {};
}

::taihe::expected<void, ::taihe::error> PrintTestInterfaceNumberi32(::optional::weak::ExampleInterface testiface)
{
    auto res = testiface->Geti32();
    if (res.has_value() && res.value().has_value()) {
        std::cout << __func__ << ": " << res.value().value() << std::endl;
    }
    return {};
}

::taihe::expected<void, ::taihe::error> PrintTestInterfaceNumberi64(::optional::weak::ExampleInterface testiface)
{
    auto res = testiface->Geti64();
    if (res.has_value() && res.value().has_value()) {
        std::cout << __func__ << ": " << res.value().value() << std::endl;
    }
    return {};
}

::taihe::expected<void, ::taihe::error> PrintTestInterfaceNumberf32(::optional::weak::ExampleInterface testiface)
{
    auto res = testiface->Getf32();
    if (res.has_value() && res.value().has_value()) {
        std::cout << __func__ << ": " << res.value().value() << std::endl;
    }
    return {};
}

::taihe::expected<void, ::taihe::error> PrintTestInterfaceNumberf64(::optional::weak::ExampleInterface testiface)
{
    auto res = testiface->Getf64();
    if (res.has_value() && res.value().has_value()) {
        std::cout << __func__ << ": " << res.value().value() << std::endl;
    }
    return {};
}

::taihe::expected<void, ::taihe::error> PrintTestInterfacebool(::optional::weak::ExampleInterface testiface)
{
    auto res = testiface->Getbool();
    if (res.has_value() && res.value().has_value()) {
        std::cout << __func__ << ": " << res.value().value() << std::endl;
    }
    return {};
}

::taihe::expected<void, ::taihe::error> PrintTestInterfaceArraybuffer(::optional::weak::ExampleInterface testiface)
{
    auto arr = testiface->GetArraybuffer();
    if (arr.has_value() && arr.value().has_value()) {
        auto const &value = arr.value().value();
        for (size_t i = 0; i < value.size(); ++i) {
            std::cout << static_cast<int>(value.data()[i]);
            if (i < value.size() - 1) {
                std::cout << ", ";
            }
        }
    }
    return {};
}
}  // namespace

// because these macros are auto-generate, lint will cause false positive.
TH_EXPORT_CPP_API_GetInterface(GetInterface);
TH_EXPORT_CPP_API_PrintTestInterfaceName(PrintTestInterfaceName);
TH_EXPORT_CPP_API_PrintTestInterfaceNumberi8(PrintTestInterfaceNumberi8);
TH_EXPORT_CPP_API_PrintTestInterfaceNumberi16(PrintTestInterfaceNumberi16);
TH_EXPORT_CPP_API_PrintTestInterfaceNumberi32(PrintTestInterfaceNumberi32);
TH_EXPORT_CPP_API_PrintTestInterfaceNumberi64(PrintTestInterfaceNumberi64);
TH_EXPORT_CPP_API_PrintTestInterfaceNumberf32(PrintTestInterfaceNumberf32);
TH_EXPORT_CPP_API_PrintTestInterfaceNumberf64(PrintTestInterfaceNumberf64);
TH_EXPORT_CPP_API_PrintTestInterfacebool(PrintTestInterfacebool);
TH_EXPORT_CPP_API_PrintTestInterfaceArraybuffer(PrintTestInterfaceArraybuffer);
// NOLINTEND