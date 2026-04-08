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

#include <taihe/runtime_ani.hpp>

#include <iostream>
#include "taihe/expected.hpp"

namespace taihe {
ani_vm *global_vm = nullptr;

void set_vm(ani_vm *vm)
{
    global_vm = vm;
}

ani_vm *get_vm()
{
    return global_vm;
}

static ani_error create_ani_error(ani_env *env, taihe::string_view msg)
{
    ani_class errCls;
    char const *className = "escompat.Error";
    if (ANI_OK != env->FindClass(className, &errCls)) {
        std::cerr << "Not found '" << className << std::endl;
        return nullptr;
    }

    ani_method errCtor;
    if (ANI_OK != env->Class_FindMethod(errCls, "<ctor>", "C{std.core.String}C{escompat.ErrorOptions}:", &errCtor)) {
        std::cerr << "Get Ctor Failed '" << className << "'" << std::endl;
        return nullptr;
    }

    ani_string result_string {};
    env->String_NewUTF8(msg.c_str(), msg.size(), &result_string);

    ani_ref undefined;
    env->GetUndefined(&undefined);

    ani_error errObj;
    if (ANI_OK != env->Object_New(errCls, errCtor, reinterpret_cast<ani_object *>(&errObj), result_string, undefined)) {
        std::cerr << "Create Object Failed '" << className << "'" << std::endl;
        return nullptr;
    }
    return errObj;
}

static ani_error create_ani_business_error(ani_env *env, int32_t code, taihe::string_view msg)
{
    ani_class errCls;
    char const *className = "@ohos.base.BusinessError";
    if (ANI_OK != env->FindClass(className, &errCls)) {
        std::cerr << "Not found '" << className << std::endl;
        return nullptr;
    }

    ani_method errCtor;
    if (ANI_OK != env->Class_FindMethod(errCls, "<ctor>", "iC{escompat.Error}:", &errCtor)) {
        std::cerr << "Get Ctor Failed '" << className << "'" << std::endl;
        return nullptr;
    }

    ani_error errObj = create_ani_error(env, msg);
    ani_int errCode = static_cast<ani_int>(code);

    ani_error businessErrObj;
    if (ANI_OK != env->Object_New(errCls, errCtor, reinterpret_cast<ani_object *>(&businessErrObj), errCode, errObj)) {
        std::cerr << "Create Object Failed '" << className << "'" << std::endl;
        return nullptr;
    }
    return businessErrObj;
}

void ani_set_error(ani_env *env, taihe::string_view msg)
{
    ani_error errObj = create_ani_error(env, msg);
    env->ThrowError(errObj);
}

void ani_set_business_error(ani_env *env, int32_t code, taihe::string_view msg)
{
    ani_error businessErrObj = create_ani_business_error(env, code, msg);
    env->ThrowError(businessErrObj);
}

void ani_reset_error(ani_env *env)
{
    env->ResetError();
}

bool ani_has_error(ani_env *env)
{
    ani_boolean res;
    env->ExistUnhandledError(&res);
    return res;
}

void set_error(taihe::string_view msg)
{
    env_guard guard;
    ani_env *env = guard.get_env();
    ani_set_error(env, msg);
}

void set_business_error(int32_t code, taihe::string_view msg)
{
    env_guard guard;
    ani_env *env = guard.get_env();
    ani_set_business_error(env, code, msg);
}

void reset_error()
{
    env_guard guard;
    ani_env *env = guard.get_env();
    ani_reset_error(env);
}

bool has_error()
{
    env_guard guard;
    ani_env *env = guard.get_env();
    return ani_has_error(env);
}

::taihe::error from_ani_error(ani_error err)
{
    env_guard guard;
    ani_env *env = guard.get_env();
    ani_string ani_error_message;
    env->Object_GetPropertyByName_Ref(ani_object(err), "message", reinterpret_cast<ani_ref *>(&ani_error_message));
    ani_size ani_error_message_len;
    env->String_GetUTF8Size(ani_error_message, &ani_error_message_len);
    TString ani_error_message_tstr;
    char *ani_error_message_buf = tstr_initialize(&ani_error_message_tstr, ani_error_message_len + 1);
    env->String_GetUTF8(ani_error_message, ani_error_message_buf, ani_error_message_len + 1, &ani_error_message_len);
    ani_error_message_buf[ani_error_message_len] = '\0';
    ani_error_message_tstr.length = ani_error_message_len;
    ::taihe::string ani_error_message_taihe = ::taihe::string(ani_error_message_tstr);
    ani_int ani_error_code = 0;
    if (ANI_OK == env->Object_GetPropertyByName_Int(err, "code", &ani_error_code)) {
        return ::taihe::error(ani_error_message_taihe, ani_error_code);
    } else {
        return ::taihe::error(ani_error_message_taihe);
    }
}

ani_error into_ani_error(::taihe::error err)
{
    env_guard guard;
    ani_env *env = guard.get_env();
    ani_string result_string {};
    env->String_NewUTF8(err.message().c_str(), err.message().size(), &result_string);
    ani_ref undefined;
    env->GetUndefined(&undefined);

    if (err.code() != 0) {
        return create_ani_business_error(env, err.code(), err.message());
    } else {
        return create_ani_error(env, err.message());
    }
}
}  // namespace taihe
