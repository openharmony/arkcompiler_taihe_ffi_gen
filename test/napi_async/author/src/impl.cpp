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

#include <async_test.impl.hpp>
#include <cstdint>
#include <iostream>
#include "taihe/napi_runtime.hpp"

namespace {
class IBaseImpl {
public:
    void makeSync()
    {
        std::cout << "make" << std::endl;
    }

    void makeRetPromise()
    {
        std::cout << "make" << std::endl;
    }

    void makeWithAsync()
    {
        std::cout << "make" << std::endl;
    }
};

int32_t addSync(int32_t a, int32_t b)
{
    if (a == 0) {
        ::taihe::set_error("some error happen");
        return b;
    } else {
        std::cout << "add impl " << a + b << std::endl;
        return a + b;
    }
}

int32_t addRetPromise(int32_t a, int32_t b)
{
    return addSync(a, b);
}

int32_t addWithAsync(int32_t a, int32_t b)
{
    return addSync(a, b);
}

::async_test::IBase createIBase()
{
    // The parameters in the make_holder function should be of the same type
    // as the parameters in the constructor of the actual implementation class.
    return taihe::make_holder<IBaseImpl, ::async_test::IBase>();
}

void printSync()
{
    std::cout << "print Sync" << std::endl;
}

void printRetPromise()
{
    printSync();
}

void printWithAsync()
{
    printSync();
}

void fromStructSync(::async_test::Data const &data)
{
    std::cout << data.a.c_str() << " " << data.b.c_str() << " " << data.c << std::endl;
    if (data.c == 0) {
        taihe::set_error("some error happen in fromStructSync_impl");
    }
    return;
}

void fromStructRetPromise(::async_test::Data const &data)
{
    fromStructSync(data);
}

void fromStructWithAsync(::async_test::Data const &data)
{
    fromStructSync(data);
}

::async_test::Data toStructSync(::taihe::string_view a, ::taihe::string_view b, int32_t c)
{
    if (c == 0) {
        taihe::set_error("some error happen in toStructSync_impl");
        return {a, b, c};
    }
    return {a, b, c};
}

::async_test::Data toStructRetPromise(::taihe::string_view a, ::taihe::string_view b, int32_t c)
{
    return toStructSync(a, b, c);
}

::async_test::Data toStructWithAsync(::taihe::string_view a, ::taihe::string_view b, int32_t c)
{
    return toStructSync(a, b, c);
}
}  // namespace

// because these macros are auto-generate, lint will cause false positive.
TH_EXPORT_CPP_API_addSync(addSync);
TH_EXPORT_CPP_API_addRetPromise(addRetPromise);
TH_EXPORT_CPP_API_addWithAsync(addWithAsync);
TH_EXPORT_CPP_API_createIBase(createIBase);
TH_EXPORT_CPP_API_printRetPromise(printRetPromise);
TH_EXPORT_CPP_API_printWithAsync(printWithAsync);
TH_EXPORT_CPP_API_printSync(printSync);
TH_EXPORT_CPP_API_fromStructRetPromise(fromStructRetPromise);
TH_EXPORT_CPP_API_fromStructWithAsync(fromStructWithAsync);
TH_EXPORT_CPP_API_fromStructSync(fromStructSync);
TH_EXPORT_CPP_API_toStructRetPromise(toStructRetPromise);
TH_EXPORT_CPP_API_toStructWithAsync(toStructWithAsync);
TH_EXPORT_CPP_API_toStructSync(toStructSync);
// NOLINTEND