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
#include "class_extends.impl.hpp"

#include "class_extends.ApplicationContext.proj.2.hpp"
#include "class_extends.BaseContext.proj.2.hpp"
#include "class_extends.Context.proj.2.hpp"
#include "class_extends.TestContext.proj.2.hpp"
#include "taihe/optional.hpp"
#include "taihe/string.hpp"
using namespace taihe;

namespace {
class ApplicationContext;

class BaseContext {
public:
    string name;

    BaseContext() : name("ApplicationContext")
    {
    }

    ~BaseContext()
    {
    }

    void setName(string_view name)
    {
        this->name = name;
    }

    string getName()
    {
        return this->name;
    }

    string getType(string_view ctxType)
    {
        return "BaseContextTypeBCTX";
    }
};

class Context {
public:
    string name;
    bool stageMode;

    Context() : name(""), stageMode(true)
    {
    }

    ~Context()
    {
    }

    void setStageMode(bool stageMode)
    {
        this->stageMode = stageMode;
    }

    bool getStageMode()
    {
        return this->stageMode;
    }

    void setName(string_view name)
    {
        this->name = name;
    }

    string getName()
    {
        return this->name;
    }

    string getType(string_view ctxType)
    {
        return "ContextTypeCTX";
    }
};

class TestContext {
public:
    string name;

    TestContext() : name("ApplicationContext")
    {
    }

    ~TestContext()
    {
    }

    void setName(string_view name)
    {
        this->name = name;
    }

    string getName()
    {
        return this->name;
    }

    string getType(string_view ctxType)
    {
        return "TestContextTCTX";
    }
};

class ApplicationContext {
public:
    string name;
    bool stageMode;

    ApplicationContext() : name("ApplicationContext"), stageMode(false)
    {
    }

    ~ApplicationContext()
    {
    }

    void setSupportedProcessCacheSync(bool isSupported)
    {
        std::cout << "setSupportedProcessCacheSync " << (isSupported ? "True" : "False") << std::endl;
    }

    void setStageMode(bool stageMode)
    {
        this->stageMode = stageMode;
    }

    bool getStageMode()
    {
        return this->stageMode;
    }

    void setName(string_view name)
    {
        this->name = name;
    }

    string getName()
    {
        return this->name;
    }

    string getType(string_view ctxType)
    {
        return "AppContextACTX";
    }
};

::class_extends::BaseContext makeBaseContext()
{
    return make_holder<BaseContext, ::class_extends::BaseContext>();
}

::class_extends::Context makeContext()
{
    return make_holder<Context, ::class_extends::Context>();
}

::class_extends::TestContext makeTestContext()
{
    return make_holder<TestContext, ::class_extends::TestContext>();
}

::class_extends::ApplicationContext makeApplicationContext()
{
    return make_holder<ApplicationContext, ::class_extends::ApplicationContext>();
}
}  // namespace

TH_EXPORT_CPP_API_makeBaseContext(makeBaseContext);
TH_EXPORT_CPP_API_makeContext(makeContext);
TH_EXPORT_CPP_API_makeTestContext(makeTestContext);
TH_EXPORT_CPP_API_makeApplicationContext(makeApplicationContext);
// NOLINTEND
