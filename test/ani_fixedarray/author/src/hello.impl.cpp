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
    taihe::array<bool> fixedArrayBoolean_ = {};
    taihe::array<double> fixedArrayNumber_ = {};
    taihe::array<::taihe::string> fixedArrayString_ = {};
    taihe::array<::hello::Data> fixedArrayData_ = {};
    taihe::optional<taihe::array<::hello::Data>> optionalFixedArrayData_;

public:
    TestInterfaceImpl()
    {
    }

    ::taihe::expected<::taihe::array<bool>, ::taihe::error> GetFixedArrayBoolean()
    {
        return fixedArrayBoolean_;
    }

    ::taihe::expected<::taihe::array<double>, ::taihe::error> GetFixedArrayNumber()
    {
        return fixedArrayNumber_;
    }

    ::taihe::expected<::taihe::array<::taihe::string>, ::taihe::error> GetFixedArrayString()
    {
        return fixedArrayString_;
    }

    ::taihe::expected<::taihe::array<::hello::Data>, ::taihe::error> GetFixedArrayData()
    {
        return fixedArrayData_;
    }

    ::taihe::expected<::taihe::optional<::taihe::array<::hello::Data>>, ::taihe::error> GetOptionalFixedArrayData()
    {
        return optionalFixedArrayData_;
    }

    ::taihe::expected<void, ::taihe::error> SetFixedArrayBoolean(::taihe::array_view<bool> value)
    {
        std::cout << "SetFixedArrayBoolean called with values: ";
        for (auto const &v : value) {
            std::cout << v << " ";
        }
        std::cout << std::endl;
        fixedArrayBoolean_ = value;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> SetFixedArrayNumber(::taihe::array_view<double> value)
    {
        std::cout << "SetFixedArrayNumber called with values: ";
        for (auto const &v : value) {
            std::cout << v << " ";
        }
        std::cout << std::endl;
        fixedArrayNumber_ = value;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> SetFixedArrayString(::taihe::array_view<::taihe::string> value)
    {
        std::cout << "SetFixedArrayString called with values: ";
        for (auto const &v : value) {
            std::cout << v << " ";
        }
        std::cout << std::endl;
        fixedArrayString_ = value;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> SetFixedArrayData(::taihe::array_view<::hello::Data> value)
    {
        std::cout << "SetFixedArrayData called with " << value.size() << " elements." << std::endl;
        fixedArrayData_ = value;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> SetOptionalFixedArrayData(
        ::taihe::optional<::taihe::array<::hello::Data>> value)
    {
        std::cout << "SetOptionalFixedArrayData called with "
                  << (value.has_value() ? std::to_string(value->size()) : "no") << " elements." << std::endl;
        optionalFixedArrayData_ = value;
        return {};
    }
};

::taihe::expected<::hello::TestInterface, ::taihe::error> NewTestInterface()
{
    // The parameters in the make_holder function should be of the same type
    // as the parameters in the constructor of the actual implementation class.
    return taihe::make_holder<TestInterfaceImpl, ::hello::TestInterface>();
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
TH_EXPORT_CPP_API_NewTestInterface(NewTestInterface);
// NOLINTEND
