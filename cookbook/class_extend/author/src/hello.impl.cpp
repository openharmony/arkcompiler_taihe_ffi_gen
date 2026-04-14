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
#include "hello.impl.hpp"
#include "hello.proj.hpp"
#include "stdexcept"
#include "taihe/object.hpp"
#include "taihe/runtime.hpp"

namespace {
class UnifiedRecord_thImpl {
public:
    UnifiedRecord_thImpl()
    {
    }

    ::taihe::expected<void, ::taihe::error> getType()
    {
        std::cout << "function GetType in UnifiedRecord_thImpl" << std::endl;
        return {};
    }
};

class Text_thImpl {
public:
    Text_thImpl()
    {
    }

    ::taihe::expected<int32_t, ::taihe::error> getDetails()
    {
        std::cout << "function GetDetails in Text_thImpl" << std::endl;
        return 1;
    }

    ::taihe::expected<void, ::taihe::error> setDetails(int32_t a)
    {
        std::cout << "function SetDetails in Text_thImpl" << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> getType()
    {
        std::cout << "function GetType in Text_thImpl" << std::endl;
        return {};
    }
};

class PlainText_thImpl {
public:
    PlainText_thImpl()
    {
    }

    ::taihe::expected<::taihe::string, ::taihe::error> getTextContent()
    {
        std::cout << "function GetTextContent in PlainText_thImpl" << std::endl;
        return "GetTextContent";
    }

    ::taihe::expected<void, ::taihe::error> setTextContent(::taihe::string_view a)
    {
        std::cout << "function SetTextContent in PlainText_thImpl" << std::endl;
        return {};
    }

    ::taihe::expected<int32_t, ::taihe::error> getDetails()
    {
        std::cout << "function GetDetails in PlainText_thImpl" << std::endl;
        return 1;
    }

    ::taihe::expected<void, ::taihe::error> setDetails(int32_t a)
    {
        std::cout << "function SetDetails in PlainText_thImpl" << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> getType()
    {
        std::cout << "function GetType in PlainText_thImpl" << std::endl;
        return {};
    }
};

class UnifiedData_thImpl {
public:
    UnifiedData_thImpl()
    {
    }

    ::taihe::expected<bool, ::taihe::error> hasType(::taihe::string_view type)
    {
        std::cout << "function HasType in UnifiedData_thImpl" << std::endl;
        return true;
    }

    ::taihe::expected<void, ::taihe::error> addRecord(::hello::weak::UnifiedRecord_th a)
    {
        std::cout << "function AddRecord in UnifiedData_thImpl" << std::endl;
        return {};
    }

    ::taihe::expected<::taihe::array<::hello::UnifiedRecord_th>, ::taihe::error> getRecords()
    {
        return ::taihe::array<::hello::UnifiedRecord_th> {
            taihe::make_holder<UnifiedRecord_thImpl, ::hello::UnifiedRecord_th>()};
    }
};

::taihe::expected<::hello::UnifiedRecord_th, ::taihe::error> createUnifiedRecord_noparam_th()
{
    return taihe::make_holder<UnifiedRecord_thImpl, ::hello::UnifiedRecord_th>();
}

::taihe::expected<::hello::Text_th, ::taihe::error> createText_noparam_th()
{
    return taihe::make_holder<Text_thImpl, ::hello::Text_th>();
}

::taihe::expected<::hello::PlainText_th, ::taihe::error> createPlainText_noparam_th()
{
    return taihe::make_holder<PlainText_thImpl, ::hello::PlainText_th>();
}

::taihe::expected<::hello::UnifiedData_th, ::taihe::error> createUnifiedData_noparam_th()
{
    return taihe::make_holder<UnifiedData_thImpl, ::hello::UnifiedData_th>();
}

::taihe::expected<::hello::UnifiedData_th, ::taihe::error> createUnifiedData_parama_th(
    ::hello::weak::UnifiedRecord_th a)
{
    return taihe::make_holder<UnifiedData_thImpl, ::hello::UnifiedData_th>();
}
}  // namespace

TH_EXPORT_CPP_API_createUnifiedRecord_noparam_th(createUnifiedRecord_noparam_th);
TH_EXPORT_CPP_API_createText_noparam_th(createText_noparam_th);
TH_EXPORT_CPP_API_createPlainText_noparam_th(createPlainText_noparam_th);
TH_EXPORT_CPP_API_createUnifiedData_noparam_th(createUnifiedData_noparam_th);
TH_EXPORT_CPP_API_createUnifiedData_parama_th(createUnifiedData_parama_th);
// NOLINTEND
