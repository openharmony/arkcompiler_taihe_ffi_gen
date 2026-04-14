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

#include "taihe/runtime.hpp"

namespace {
::taihe::expected<int32_t, ::taihe::error> add_impl(int32_t a, int32_t b)
{
    if (a == 0) {
        return ::taihe::unexpected<::taihe::error>(::taihe::error("some error happen in add impl", 1));
    } else {
        std::cout << "add impl " << a + b << std::endl;
        return a + b;
    }
}

::taihe::expected<::async_test::IBase, ::taihe::error> getIBase_impl()
{
    struct AuthorIBase {
        taihe::string name;

        AuthorIBase() : name("My IBase")
        {
        }

        ~AuthorIBase()
        {
        }

        ::taihe::expected<::taihe::string, ::taihe::error> get()
        {
            return name;
        }

        ::taihe::expected<void, ::taihe::error> set(taihe::string_view a)
        {
            this->name = a;
            return {};
        }

        ::taihe::expected<void, ::taihe::error> makeSync()
        {
            TH_THROW(std::runtime_error, "makeSync not implemented");
            return {};
        }
    };

    return taihe::make_holder<AuthorIBase, ::async_test::IBase>();
}

::taihe::expected<void, ::taihe::error> fromStructSync_impl(::async_test::Data const &data)
{
    std::cout << data.a.c_str() << " " << data.b.c_str() << " " << data.c << std::endl;
    if (data.c == 0) {
        return ::taihe::unexpected<::taihe::error>(::taihe::error("some error happen in fromStructSync_impl", 1));
    }
    return {};
}

::taihe::expected<::async_test::Data, ::taihe::error> toStructSync_impl(taihe::string_view a, taihe::string_view b,
                                                                        int32_t c)
{
    if (c == 0) {
        return ::taihe::unexpected<::taihe::error>(::taihe::error("some error happen in toStructSync_impl", 1));
    }
    return ::async_test::Data {a, b, c};
}

::taihe::expected<void, ::taihe::error> PrintSync()
{
    std::cout << "print Sync" << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> makeGlobalSync()
{
    TH_THROW(std::runtime_error, "makeGlobalSync not implemented");
    return {};
}
}  // namespace

// because these macros are auto-generate, lint will cause false positive.
TH_EXPORT_CPP_API_addSync(add_impl);
TH_EXPORT_CPP_API_getIBase(getIBase_impl);
TH_EXPORT_CPP_API_fromStructSync(fromStructSync_impl);
TH_EXPORT_CPP_API_toStructSync(toStructSync_impl);
TH_EXPORT_CPP_API_PrintSync(PrintSync);
TH_EXPORT_CPP_API_makeGlobalSync(makeGlobalSync);
// NOLINTEND