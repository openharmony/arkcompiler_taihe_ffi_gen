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
#include "rename_example.impl.hpp"
#include "rename_example.proj.hpp"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace rename_example;

namespace {

// C++ side always uses original names
int32_t OldFoo(int32_t a, int32_t b)
{
    return a + b;
}

OldPoint CreatePoint(int32_t x, int32_t y)
{
    return {x, y};
}

class OldGreeterImpl {
    string name_;

public:
    OldGreeterImpl(string_view name) : name_(name)
    {
    }

    string Greet()
    {
        return "Hello from " + name_;
    }
};

OldGreeter CreateGreeter(string_view name)
{
    return make_holder<OldGreeterImpl, OldGreeter>(name);
}

::taihe::string TestParamRename(::taihe::string_view msg)
{
    return "Received message: " + msg;
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

OldMyInterface MyInterfaceCtor()
{
    return taihe::make_holder<OldMyInterfaceImpl, OldMyInterface>();
}

}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
TH_EXPORT_CPP_API_OldFoo(OldFoo);
TH_EXPORT_CPP_API_CreatePoint(CreatePoint);
TH_EXPORT_CPP_API_CreateGreeter(CreateGreeter);
TH_EXPORT_CPP_API_TestParamRename(TestParamRename);
TH_EXPORT_CPP_API_MyStructStaticFunc(MyStructStaticFunc);
TH_EXPORT_CPP_API_MyInterfaceCtor(MyInterfaceCtor);
// NOLINTEND
