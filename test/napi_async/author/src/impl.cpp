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
#include <thread>

namespace {
class IBaseImpl {
public:
    ::taihe::expected<void, ::taihe::error> makeSync()
    {
        std::cout << "makeSync" << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> makeRetPromise()
    {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        std::cout << "makeRetPromise" << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> makeWithAsync()
    {
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
        std::cout << "makeWithAsync" << std::endl;
        return {};
    }
};

class IShapeImpl {
public:
    ::taihe::expected<void, ::taihe::error> makeSync()
    {
        std::cout << "make In shape" << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> makeRetPromise()
    {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        std::cout << "make In shape RetPromise" << std::endl;
        return ::taihe::expected<void, ::taihe::error>(::taihe::unexpect, "Error in makeRetPromise", 1);
    }

    ::taihe::expected<void, ::taihe::error> makeWithAsync()
    {
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
        std::cout << "make In shape WithAsync" << std::endl;
        return ::taihe::expected<void, ::taihe::error>(::taihe::unexpect, "Error in makeWithAsync", 2);
    }
};

::taihe::expected<int32_t, ::taihe::error> addSync(int32_t a, int32_t b)
{
    if (a == 0) {
        std::cout << "throw error in addSync impl " << std::endl;
        return ::taihe::expected<int32_t, ::taihe::error>(::taihe::unexpect, "some error happen");
    } else {
        std::cout << "add impl " << a + b << std::endl;
        return a + b;
    }
}

::taihe::expected<int32_t, ::taihe::error> addRetPromise(int32_t a, int32_t b)
{
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    if (a == 0) {
        std::cout << "ERROR in addRetPromise" << std::endl;
        return ::taihe::expected<int32_t, ::taihe::error>(::taihe::unexpect, "some error happen");
    } else {
        std::cout << "SUCCESS in addRetPromise: " << a + b << std::endl;
        return a + b;
    }
}

::taihe::expected<int32_t, ::taihe::error> addWithAsync(int32_t a, int32_t b)
{
    std::this_thread::sleep_for(std::chrono::milliseconds(50));

    if (a == 0) {
        std::cout << "ERROR in addWithAsync" << std::endl;
        return ::taihe::expected<int32_t, ::taihe::error>(::taihe::unexpect, "some error happen");
    } else {
        std::cout << "SUCCESS in addWithAsync: " << a + b << std::endl;
        return a + b;
    }
}

::taihe::expected<::async_test::IBase, ::taihe::error> createIBase()
{
    // The parameters in the make_holder function should be of the same type
    // as the parameters in the constructor of the actual implementation class.
    return taihe::make_holder<IBaseImpl, ::async_test::IBase>();
}

::taihe::expected<void, ::taihe::error> printSync()
{
    std::cout << "print Sync" << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> printRetPromise()
{
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    std::cout << "printRetPromise" << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> printWithAsync()
{
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    std::cout << "printWithAsync" << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> fromStructSync(::async_test::Data const &data)
{
    std::cout << "fromStructSync" << data.a.c_str() << " " << data.b.c_str() << " " << data.c << std::endl;
    if (data.c == 0) {
        return ::taihe::expected<void, ::taihe::error>(::taihe::unexpect, "some error happen in fromStructSync");
    }
    return {};
}

::taihe::expected<void, ::taihe::error> fromStructRetPromise(::async_test::Data const &data)
{
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    std::cout << "fromStructRetPromise" << data.a.c_str() << " " << data.b.c_str() << " " << data.c << std::endl;
    if (data.c == 0) {
        return ::taihe::expected<void, ::taihe::error>(::taihe::unexpect, "some error happen in fromStructRetPromise");
    }
    return {};
}

::taihe::expected<void, ::taihe::error> fromStructWithAsync(::async_test::Data const &data)
{
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    std::cout << "fromStructWithAsync" << data.a.c_str() << " " << data.b.c_str() << " " << data.c << std::endl;
    if (data.c == 0) {
        return ::taihe::expected<void, ::taihe::error>(::taihe::unexpect, "some error happen in fromStructWithAsync");
    }
    return {};
}

::taihe::expected<::async_test::Data, ::taihe::error> toStructSync(::taihe::string_view a, ::taihe::string_view b,
                                                                   int32_t c)
{
    if (c == 0) {
        return ::taihe::expected<::async_test::Data, ::taihe::error>(::taihe::unexpect,
                                                                     "some error happen in toStructSync");
    }
    return ::async_test::Data {a, b, c};
}

::taihe::expected<::async_test::Data, ::taihe::error> toStructRetPromise(::taihe::string_view a, ::taihe::string_view b,
                                                                         int32_t c)
{
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    if (c == 0) {
        return ::taihe::expected<::async_test::Data, ::taihe::error>(::taihe::unexpect,
                                                                     "some error happen in toStructRetPromise");
    }
    return ::async_test::Data {a, b, c};
}

::taihe::expected<::async_test::Data, ::taihe::error> toStructWithAsync(::taihe::string_view a, ::taihe::string_view b,
                                                                        int32_t c)
{
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    if (c == 0) {
        return ::taihe::expected<::async_test::Data, ::taihe::error>(::taihe::unexpect,
                                                                     "some error happen in toStructWithAsync");
    }
    return ::async_test::Data {a, b, c};
}

::taihe::expected<::async_test::IShape, ::taihe::error> createIShape()
{
    // The parameters in the make_holder function should be of the same type
    // as the parameters in the constructor of the actual implementation class.
    return taihe::make_holder<IShapeImpl, ::async_test::IShape>();
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
TH_EXPORT_CPP_API_createIShape(createIShape);
// NOLINTEND