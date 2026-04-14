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
#include "import_example.impl.hpp"
#include <iostream>
#include "import_example.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

namespace {
// To be implemented.

constexpr int K_DEFAULT_X = 1;
constexpr int K_DEFAULT_Y = 2;

constexpr int K_ID = 1;
constexpr char const *K_NAME = "1";

class IfaceAImpl {
public:

public:
    IfaceAImpl()
    {
    }

    ::taihe::expected<void, ::taihe::error> Foo()
    {
        std::cout << "Export IfaceA Foo()" << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Bar()
    {
        std::cout << "Export IfaceA Bar()" << std::endl;
        return {};
    }
};

::taihe::expected<::export_enum::ExportEnum, ::taihe::error> ImportEnumFunc()
{
    return ::export_enum::ExportEnum::key_t::Foo;
}

::taihe::expected<::export_iface::IfaceA, ::taihe::error> ImportIfaceFunc()
{
    return taihe::make_holder<IfaceAImpl, ::export_iface::IfaceA>();
}

::taihe::expected<::export_namespace::NsStructA, ::taihe::error> ImportNsFunc()
{
    return ::export_namespace::NsStructA {K_DEFAULT_X, K_DEFAULT_Y};
}

::taihe::expected<::export_struct::StructA, ::taihe::error> ImportStructFunc()
{
    return ::export_struct::StructA {K_ID, K_NAME};
}

::taihe::expected<::export_union::ExportUnion, ::taihe::error> ImportUnionFunc()
{
    return ::export_union::ExportUnion::make_Foo(K_NAME);
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
TH_EXPORT_CPP_API_ImportEnumFunc(ImportEnumFunc);
TH_EXPORT_CPP_API_ImportIfaceFunc(ImportIfaceFunc);
TH_EXPORT_CPP_API_ImportNsFunc(ImportNsFunc);
TH_EXPORT_CPP_API_ImportStructFunc(ImportStructFunc);
TH_EXPORT_CPP_API_ImportUnionFunc(ImportUnionFunc);
// NOLINTEND
