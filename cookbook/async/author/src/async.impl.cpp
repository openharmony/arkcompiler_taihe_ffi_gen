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
#include "async.impl.hpp"

#include "async.IStringHolder.proj.2.hpp"
#include "stdexcept"
#include "taihe/string.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {
class IStringHolder {
public:
    IStringHolder() : str("MyStr")
    {
    }

    ~IStringHolder()
    {
    }

    string getStrSync()
    {
        return str;
    }

    ::taihe::string getStrWithAsync()
    {
        return str;
    }

    ::taihe::string getStrRetPromise()
    {
        return str;
    }

    void setStrSync(string_view a)
    {
        this->str = a;
    }

    void setStrWithAsync(::taihe::string_view a)
    {
        this->str = a;
    }

    void setStrRetPromise(::taihe::string_view a)
    {
        this->str = a;
    }

private:
    string str;
};

int32_t addSync(int32_t a, int32_t b)
{
    return a + b;
}

::async::IStringHolder makeIStringHolder()
{
    return make_holder<IStringHolder, ::async::IStringHolder>();
}
}  // namespace

TH_EXPORT_CPP_API_addAsync(addSync);
TH_EXPORT_CPP_API_addPromise(addSync);
TH_EXPORT_CPP_API_addSync(addSync);
TH_EXPORT_CPP_API_makeIStringHolder(makeIStringHolder);
// NOLINTEND
