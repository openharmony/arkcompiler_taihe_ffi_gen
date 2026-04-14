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
#include "struct_test.impl.hpp"
#include "stdexcept"
#include "struct_test.proj.hpp"
#include "taihe/runtime.hpp"

using namespace taihe;

namespace {
// To be implemented.

class StructDImpl {
public:
    ::struct_test::DBase5 structD = {1, 2, 3, 4, "5"};

    StructDImpl()
    {
    }

    ::taihe::expected<void, ::taihe::error> SetStructD(::struct_test::DBase5 const &d)
    {
        this->structD = d;
        return {};
    }

    ::taihe::expected<::struct_test::DBase5, ::taihe::error> GetStructD()
    {
        return structD;
    }
};

class StructEImpl {
public:
    ::struct_test::EBigint structE = {true, 5.17, 18.00, 2025};

    StructEImpl()
    {
    }

    ::taihe::expected<void, ::taihe::error> SetStructE(::struct_test::EBigint const &e)
    {
        this->structE = e;
        return {};
    }

    ::taihe::expected<::struct_test::EBigint, ::taihe::error> GetStructE()
    {
        return structE;
    }
};

class StructFImpl {
public:
    ::struct_test::FUnion structF;

    StructFImpl()
        : structF({taihe::optional<taihe::string>(std::in_place_t {}, "optval"),
                   ::struct_test::UnionF::make_sValue("unionval"), taihe::map<taihe::string, taihe::string>()})
    {
        this->structF.param3.emplace("rsK", "rsV");
    }

    ::taihe::expected<void, ::taihe::error> SetStructF(::struct_test::FUnion const &f)
    {
        this->structF = f;
        return {};
    }

    ::taihe::expected<::struct_test::FUnion, ::taihe::error> GetStructF()
    {
        return structF;
    }
};

class StructGImpl {
public:
    ::struct_test::GArray gArray = {{1, 2, 3, 4, 5}, {1, 2, 3, 4, 5}};

    StructGImpl()
    {
    }

    ::taihe::expected<void, ::taihe::error> SetGArray(::struct_test::GArray const &sa)
    {
        this->gArray = sa;
        return {};
    }

    ::taihe::expected<::struct_test::GArray, ::taihe::error> GetGArray()
    {
        return gArray;
    }
};

class SDB5ReadonlyImpl {
public:
    ::struct_test::DB5Readonly db5 = {1, 2, 3, 4, "5"};

    SDB5ReadonlyImpl()
    {
    }

    ::taihe::expected<void, ::taihe::error> SetDB5Readonly(::struct_test::DB5Readonly const &d)
    {
        this->db5 = d;
        return {};
    }

    ::taihe::expected<::struct_test::DB5Readonly, ::taihe::error> GetDB5Readonly()
    {
        return db5;
    }
};

class SEBReadonlyImpl {
public:
    ::struct_test::EBigintReadonly ebr = {true, 5.17, 18.00, 2025};

    SEBReadonlyImpl()
    {
    }

    ::taihe::expected<void, ::taihe::error> SetSEBReadonly(::struct_test::EBigintReadonly const &e)
    {
        this->ebr = e;
        return {};
    }

    ::taihe::expected<::struct_test::EBigintReadonly, ::taihe::error> GetSEBReadonly()
    {
        return ebr;
    }
};

::taihe::expected<::struct_test::StructD, ::taihe::error> GetStructD()
{
    return taihe::make_holder<StructDImpl, ::struct_test::StructD>();
}

::taihe::expected<::struct_test::StructE, ::taihe::error> GetStructE()
{
    return taihe::make_holder<StructEImpl, ::struct_test::StructE>();
}

::taihe::expected<::struct_test::StructF, ::taihe::error> GetStructF()
{
    return taihe::make_holder<StructFImpl, ::struct_test::StructF>();
}

::taihe::expected<::struct_test::StructG, ::taihe::error> GetStructG()
{
    return taihe::make_holder<StructGImpl, ::struct_test::StructG>();
}

::taihe::expected<::struct_test::Canvas, ::taihe::error> addNewCanvas(::taihe::string_view name)
{
    return ::struct_test::Canvas {{255, 0, 255}, name};
}

::taihe::expected<::struct_test::SDB5Readonly, ::taihe::error> GetSDB5Readonly()
{
    return taihe::make_holder<SDB5ReadonlyImpl, ::struct_test::SDB5Readonly>();
}

::taihe::expected<::struct_test::SEBReadonly, ::taihe::error> GetSEBReadonly()
{
    return taihe::make_holder<SEBReadonlyImpl, ::struct_test::SEBReadonly>();
}

::taihe::expected<::struct_test::Draw, ::taihe::error> AddNewDraw(::taihe::string_view drawName)
{
    return ::struct_test::Draw {{255, 0, 255}, drawName};
}

::taihe::expected<::struct_test::Student, ::taihe::error> create_student()
{
    return ::struct_test::Student {"Mary", 15};
}

::taihe::expected<::struct_test::Student, ::taihe::error> process_student(::struct_test::Student const &a)
{
    return ::struct_test::Student {a.name + " student", a.age + 10};
}

::taihe::expected<::struct_test::Teacher, ::taihe::error> create_teacher()
{
    return ::struct_test::Teacher {"Rose", 25};
}

::taihe::expected<::struct_test::Teacher, ::taihe::error> process_teacher(::struct_test::Teacher const &a)
{
    return ::struct_test::Teacher {a.name + " teacher", a.age + 15};
}

::taihe::expected<::struct_test::G, ::taihe::error> process_g(::struct_test::G const &a)
{
    return ::struct_test::G {{a.f.f + 1}, a.g + 2};
}

::taihe::expected<::struct_test::H, ::taihe::error> process_h(::struct_test::H const &a)
{
    return ::struct_test::H {{{a.g.f.f + 1}, a.g.g + 2}, a.h + 3};
}
}  // namespace

TH_EXPORT_CPP_API_GetStructD(GetStructD);
TH_EXPORT_CPP_API_GetStructE(GetStructE);
TH_EXPORT_CPP_API_GetStructF(GetStructF);
TH_EXPORT_CPP_API_GetStructG(GetStructG);
TH_EXPORT_CPP_API_addNewCanvas(addNewCanvas);
TH_EXPORT_CPP_API_GetSDB5Readonly(GetSDB5Readonly);
TH_EXPORT_CPP_API_GetSEBReadonly(GetSEBReadonly);
TH_EXPORT_CPP_API_AddNewDraw(AddNewDraw);
TH_EXPORT_CPP_API_create_student(create_student);
TH_EXPORT_CPP_API_process_student(process_student);
TH_EXPORT_CPP_API_create_teacher(create_teacher);
TH_EXPORT_CPP_API_process_teacher(process_teacher);
TH_EXPORT_CPP_API_process_g(process_g);
TH_EXPORT_CPP_API_process_h(process_h);
// NOLINTEND
