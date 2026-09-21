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
    taihe::array<int32_t> valueArrayInt_ = {};
    taihe::array<double> valueArrayDouble_ = {};
    taihe::array<bool> valueArrayBoolean_ = {};

public:
    TestInterfaceImpl()
    {
    }

    ::taihe::expected<::taihe::array<int32_t>, ::taihe::error> GetValueArrayInt()
    {
        return valueArrayInt_;
    }

    ::taihe::expected<::taihe::array<double>, ::taihe::error> GetValueArrayDouble()
    {
        return valueArrayDouble_;
    }

    ::taihe::expected<::taihe::array<bool>, ::taihe::error> GetValueArrayBoolean()
    {
        return valueArrayBoolean_;
    }

    ::taihe::expected<void, ::taihe::error> SetValueArrayInt(::taihe::array_view<int32_t> value)
    {
        std::cout << "SetValueArrayInt called with values: ";
        for (auto const &v : value) {
            std::cout << v << " ";
        }
        std::cout << std::endl;
        valueArrayInt_ = value;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> SetValueArrayDouble(::taihe::array_view<double> value)
    {
        std::cout << "SetValueArrayDouble called with values: ";
        for (auto const &v : value) {
            std::cout << v << " ";
        }
        std::cout << std::endl;
        valueArrayDouble_ = value;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> SetValueArrayBoolean(::taihe::array_view<bool> value)
    {
        std::cout << "SetValueArrayBoolean called with values: ";
        for (auto const &v : value) {
            std::cout << v << " ";
        }
        std::cout << std::endl;
        valueArrayBoolean_ = value;
        return {};
    }
};

::taihe::expected<::hello::TestInterface, ::taihe::error> NewTestInterface()
{
    return taihe::make_holder<TestInterfaceImpl, ::hello::TestInterface>();
}
}  // namespace

TH_EXPORT_CPP_API_NewTestInterface(NewTestInterface);
// NOLINTEND