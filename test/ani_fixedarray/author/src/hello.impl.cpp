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
#include "hello.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

namespace {
class TestInterfaceImpl {
    taihe::array<bool> m_fixedArrayBoolean = {};
    taihe::array<double> m_fixedArrayNumber = {};
    taihe::array<::taihe::string> m_fixedArrayString = {};
    taihe::array<::hello::Data> m_fixedArrayData = {};
    taihe::optional<taihe::array<::hello::Data>> m_optionalFixedArrayData;
    taihe::array<int32_t> m_valueArrayInt = {};
    taihe::array<double> m_valueArrayDouble = {};

public:
    TestInterfaceImpl()
    {
    }

    ::taihe::expected<::taihe::array<bool>, ::taihe::error> getFixedArrayBoolean()
    {
        return m_fixedArrayBoolean;
    }

    ::taihe::expected<::taihe::array<double>, ::taihe::error> getFixedArrayNumber()
    {
        return m_fixedArrayNumber;
    }

    ::taihe::expected<::taihe::array<::taihe::string>, ::taihe::error> getFixedArrayString()
    {
        return m_fixedArrayString;
    }

    ::taihe::expected<::taihe::array<::hello::Data>, ::taihe::error> getFixedArrayData()
    {
        return m_fixedArrayData;
    }

    ::taihe::expected<::taihe::optional<::taihe::array<::hello::Data>>, ::taihe::error> getOptionalFixedArrayData()
    {
        return m_optionalFixedArrayData;
    }

    ::taihe::expected<::taihe::array<int32_t>, ::taihe::error> getValueArrayInt()
    {
        return m_valueArrayInt;
    }

    ::taihe::expected<::taihe::array<double>, ::taihe::error> getValueArrayDouble()
    {
        return m_valueArrayDouble;
    }

    ::taihe::expected<void, ::taihe::error> setFixedArrayBoolean(::taihe::array_view<bool> value)
    {
        std::cout << "setFixedArrayBoolean called with values: ";
        for (auto const &v : value) {
            std::cout << v << " ";
        }
        std::cout << std::endl;
        m_fixedArrayBoolean = value;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> setFixedArrayNumber(::taihe::array_view<double> value)
    {
        std::cout << "setFixedArrayNumber called with values: ";
        for (auto const &v : value) {
            std::cout << v << " ";
        }
        std::cout << std::endl;
        m_fixedArrayNumber = value;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> setFixedArrayString(::taihe::array_view<::taihe::string> value)
    {
        std::cout << "setFixedArrayString called with values: ";
        for (auto const &v : value) {
            std::cout << v << " ";
        }
        std::cout << std::endl;
        m_fixedArrayString = value;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> setFixedArrayData(::taihe::array_view<::hello::Data> value)
    {
        std::cout << "setFixedArrayData called with " << value.size() << " elements." << std::endl;
        m_fixedArrayData = value;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> setOptionalFixedArrayData(
        ::taihe::optional<::taihe::array<::hello::Data>> value)
    {
        std::cout << "setOptionalFixedArrayData called with "
                  << (value.has_value() ? std::to_string(value->size()) : "no") << " elements." << std::endl;
        m_optionalFixedArrayData = value;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> setValueArrayInt(::taihe::array_view<int32_t> value)
    {
        std::cout << "setValueArrayInt called with values: ";
        for (auto const &v : value) {
            std::cout << v << " ";
        }
        std::cout << std::endl;
        m_valueArrayInt = value;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> setValueArrayDouble(::taihe::array_view<double> value)
    {
        std::cout << "setValueArrayDouble called with values: ";
        for (auto const &v : value) {
            std::cout << v << " ";
        }
        std::cout << std::endl;
        m_valueArrayDouble = value;
        return {};
    }
};

::taihe::expected<::hello::TestInterface, ::taihe::error> newTestInterface()
{
    // The parameters in the make_holder function should be of the same type
    // as the parameters in the constructor of the actual implementation class.
    return taihe::make_holder<TestInterfaceImpl, ::hello::TestInterface>();
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
TH_EXPORT_CPP_API_newTestInterface(newTestInterface);
// NOLINTEND
