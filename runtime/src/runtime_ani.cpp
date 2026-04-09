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

#include <taihe/expected.hpp>
#include <taihe/runtime_ani.hpp>

#include <iostream>

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
    char const *className = "std.core.Error";
    if (ANI_OK != env->FindClass(className, &errCls)) {
        std::cerr << "Not found '" << className << std::endl;
        return nullptr;
    }

    ani_method errCtor;
    if (ANI_OK != env->Class_FindMethod(errCls, "<ctor>", "C{std.core.String}C{std.core.ErrorOptions}:", &errCtor)) {
        std::cerr << "Get Ctor Failed '" << className << "'" << std::endl;
        return nullptr;
    }

    ani_string errMsg {};
    env->String_NewUTF8(msg.c_str(), msg.size(), &errMsg);

    ani_ref undefined;
    env->GetUndefined(&undefined);

    ani_error errObj;
    if (ANI_OK != env->Object_New(errCls, errCtor, reinterpret_cast<ani_object *>(&errObj), errMsg, undefined)) {
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
    if (ANI_OK != env->Class_FindMethod(errCls, "<ctor>", "iC{std.core.Error}:", &errCtor)) {
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

ani_error take_ani_error(ani_env *env)
{
    ani_boolean hasErr;
    env->ExistUnhandledError(&hasErr);
    if (hasErr) {
        ani_error errObj;
        env->GetUnhandledError(&errObj);
        env->ResetError();
        return errObj;
    } else {
        return nullptr;
    }
}

taihe::error from_ani_error(ani_env *env, ani_error errObj)
{
    ani_string errMsg {};
    env->Object_GetPropertyByName_Ref(ani_object(errObj), "message", reinterpret_cast<ani_ref *>(&errMsg));
    ani_size msgLength;
    env->String_GetUTF8Size(errMsg, &msgLength);
    TString msgHandle;
    char *msgBuffer = tstr_initialize(&msgHandle, msgLength + 1);
    env->String_GetUTF8(errMsg, msgBuffer, msgLength + 1, &msgLength);
    msgBuffer[msgLength] = '\0';
    msgHandle.length = msgLength;
    taihe::string msg(msgHandle);

    ani_int code = 0;
    if (ANI_OK == env->Object_GetPropertyByName_Int(errObj, "code", &code)) {
        return taihe::error(msg, code);
    } else {
        return taihe::error(msg);
    }
}

ani_error into_ani_error(ani_env *env, taihe::error err)
{
    if (err.code() != 0) {
        return create_ani_business_error(env, err.code(), err.message());
    } else {
        return create_ani_error(env, err.message());
    }
}

void make_ani_error(ani_env *env, taihe::error err)
{
    ani_error errObj = into_ani_error(env, err);
    env->ThrowError(errObj);
}
}  // namespace taihe
