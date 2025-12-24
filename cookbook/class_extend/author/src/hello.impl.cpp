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

    void getType()
    {
        std::cout << "function GetType in UnifiedRecord_thImpl" << std::endl;
    }
};

class Text_thImpl {
public:
    Text_thImpl()
    {
    }

    int32_t getDetails()
    {
        std::cout << "function GetDetails in Text_thImpl" << std::endl;
        return 1;
    }

    void setDetails(int32_t a)
    {
        std::cout << "function SetDetails in Text_thImpl" << std::endl;
    }

    void getType()
    {
        std::cout << "function GetType in Text_thImpl" << std::endl;
    }
};

class PlainText_thImpl {
public:
    PlainText_thImpl()
    {
    }

    ::taihe::string getTextContent()
    {
        std::cout << "function GetTextContent in PlainText_thImpl" << std::endl;
        return "GetTextContent";
    }

    void setTextContent(::taihe::string_view a)
    {
        std::cout << "function SetTextContent in PlainText_thImpl" << std::endl;
    }

    int32_t getDetails()
    {
        std::cout << "function GetDetails in PlainText_thImpl" << std::endl;
        return 1;
    }

    void setDetails(int32_t a)
    {
        std::cout << "function SetDetails in PlainText_thImpl" << std::endl;
    }

    void getType()
    {
        std::cout << "function GetType in PlainText_thImpl" << std::endl;
    }
};

class UnifiedData_thImpl {
public:
    UnifiedData_thImpl()
    {
    }

    bool hasType(::taihe::string_view type)
    {
        std::cout << "function HasType in UnifiedData_thImpl" << std::endl;
    }

    void addRecord(::hello::weak::UnifiedRecord_th a)
    {
        std::cout << "function AddRecord in UnifiedData_thImpl" << std::endl;
    }

    ::taihe::array<::hello::UnifiedRecord_th> getRecords()
    {
        return ::taihe::array<::hello::UnifiedRecord_th> {
            taihe::make_holder<UnifiedRecord_thImpl, ::hello::UnifiedRecord_th>()};
    }
};

::hello::UnifiedRecord_th createUnifiedRecord_noparam_th()
{
    return taihe::make_holder<UnifiedRecord_thImpl, ::hello::UnifiedRecord_th>();
}

::hello::Text_th createText_noparam_th()
{
    return taihe::make_holder<Text_thImpl, ::hello::Text_th>();
}

::hello::PlainText_th createPlainText_noparam_th()
{
    return taihe::make_holder<PlainText_thImpl, ::hello::PlainText_th>();
}

::hello::UnifiedData_th createUnifiedData_noparam_th()
{
    return taihe::make_holder<UnifiedData_thImpl, ::hello::UnifiedData_th>();
}

::hello::UnifiedData_th createUnifiedData_parama_th(::hello::weak::UnifiedRecord_th a)
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
