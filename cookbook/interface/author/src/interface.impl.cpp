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
#include "interface.impl.hpp"

#include "interface.ICalculator.proj.2.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {

class MyCalculator {
public:
    MyCalculator(int32_t init) : lastResult(init)
    {
    }

    ::taihe::expected<int32_t, ::taihe::error> add(int32_t a, int32_t b)
    {
        lastResult = a + b;
        return lastResult;
    }

    ::taihe::expected<int32_t, ::taihe::error> sub(int32_t a, int32_t b)
    {
        lastResult = a - b;
        return lastResult;
    }

    ::taihe::expected<int32_t, ::taihe::error> getLastResult()
    {
        return lastResult;
    }

    ::taihe::expected<void, ::taihe::error> reset()
    {
        lastResult = 0;
        return {};
    }

private:
    int32_t lastResult = 0;
};

::taihe::expected<::interface::ICalculator, ::taihe::error> makeCalculator()
{
    return make_holder<MyCalculator, ::interface::ICalculator>(0);
}

::taihe::expected<void, ::taihe::error> restartCalculator(::interface::weak::ICalculator a)
{
    a->reset();
    return {};
}

}  // namespace

TH_EXPORT_CPP_API_makeCalculator(makeCalculator);
TH_EXPORT_CPP_API_restartCalculator(restartCalculator);
// NOLINTEND
