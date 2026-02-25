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
#include "rename_test.impl.hpp"
#include "rename_test.proj.hpp"
#include "taihe/runtime.hpp"
#include <iostream>

using namespace taihe;
using namespace rename_test;

namespace {

// C++ side uses original names

int32_t OldAdd(int32_t a, int32_t b)
{
    return a + b;
}

int32_t GetColorValue(OldColor c)
{
    return c.get_value();
}

OldPoint CreatePoint(int32_t x, int32_t y)
{
    return {x, y};
}

int32_t GetPointSum(OldPoint const &p)
{
    return p.x + p.y;
}

class OldCalculatorImpl {
public:
    int32_t OldCompute(int32_t a, int32_t b)
    {
        return a * b;
    }
};

OldCalculator CreateCalculator()
{
    return make_holder<OldCalculatorImpl, OldCalculator>();
}

OldData CreateIntData(int32_t v)
{
    return OldData::make_intVal(v);
}

OldData CreateStrData(string_view v)
{
    return OldData::make_strVal(v);
}

OldMyStruct MyStructCtor(unit dummy, int32_t a, string_view b)
{
    return OldMyStruct {a, b};
}

string MyStructStaticFunc()
{
    return "Hello from MyStructStaticFunc";
}

class OldMyInterfaceImpl {
public:
    std::string doSomething(string_view s)
    {
        return "Hello, " + std::string(s);
    }
};

OldMyInterface MyInterfaceCtor(unit dummy)
{
    return taihe::make_holder<OldMyInterfaceImpl, OldMyInterface>();
}

string MyInterfaceStaticMethod()
{
    return "Hello from MyInterfaceStaticMethod";
}
}  // namespace

TH_EXPORT_CPP_API_OldAdd(OldAdd);
TH_EXPORT_CPP_API_GetColorValue(GetColorValue);
TH_EXPORT_CPP_API_CreatePoint(CreatePoint);
TH_EXPORT_CPP_API_GetPointSum(GetPointSum);
TH_EXPORT_CPP_API_CreateCalculator(CreateCalculator);
TH_EXPORT_CPP_API_CreateIntData(CreateIntData);
TH_EXPORT_CPP_API_CreateStrData(CreateStrData);
TH_EXPORT_CPP_API_MyStructCtor(MyStructCtor);
TH_EXPORT_CPP_API_MyStructStaticFunc(MyStructStaticFunc);
TH_EXPORT_CPP_API_MyInterfaceCtor(MyInterfaceCtor);
TH_EXPORT_CPP_API_MyInterfaceStaticMethod(MyInterfaceStaticMethod);
// NOLINTEND
