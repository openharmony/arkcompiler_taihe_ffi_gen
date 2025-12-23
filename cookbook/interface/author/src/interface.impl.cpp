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

    int32_t add(int32_t a, int32_t b)
    {
        lastResult = a + b;
        return lastResult;
    }

    int32_t sub(int32_t a, int32_t b)
    {
        lastResult = a - b;
        return lastResult;
    }

    int32_t getLastResult()
    {
        return lastResult;
    }

    void reset()
    {
        lastResult = 0;
    }

private:
    int32_t lastResult = 0;
};

::interface::ICalculator makeCalculator()
{
    return make_holder<MyCalculator, ::interface::ICalculator>(0);
}

void restartCalculator(::interface::weak::ICalculator a)
{
    a->reset();
}

}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_makeCalculator(makeCalculator);
TH_EXPORT_CPP_API_restartCalculator(restartCalculator);
// NOLINTEND
