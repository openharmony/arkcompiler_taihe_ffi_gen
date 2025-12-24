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
#include "extends_inject.impl.hpp"

#include "extends_inject.InnerPerson.proj.2.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {
class InnerPerson {
public:
    uintptr_t getPseron()
    {
        ani_long ani_vtbl_ptr;
        ani_long ani_data_ptr;
        ani_class ani_obj_cls;
        ani_env *env = get_env();
        env->FindClass("Person.Person", &ani_obj_cls);
        ani_method ani_obj_ctor;
        env->Class_FindMethod(ani_obj_cls, "<ctor>", nullptr, &ani_obj_ctor);
        ani_object ani_obj;
        env->Object_New(ani_obj_cls, ani_obj_ctor, &ani_obj, ani_vtbl_ptr, ani_data_ptr);
        return reinterpret_cast<uintptr_t>(ani_obj);
    }

    ::extends_inject::InnerPerson getInnerPerson()
    {
        return make_holder<InnerPerson, ::extends_inject::InnerPerson>();
    }
};

::extends_inject::InnerPerson makePerson()
{
    return make_holder<InnerPerson, ::extends_inject::InnerPerson>();
}
}  // namespace

TH_EXPORT_CPP_API_makePerson(makePerson);
// NOLINTEND
