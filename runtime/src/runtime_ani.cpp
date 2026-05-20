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

#ifdef TH_ANI_USE_LOCAL_TRACE
#include <chrono>
#include <vector>

namespace {
thread_local std::vector<std::pair<char const *, std::chrono::steady_clock::time_point>> ani_perf_trace_stack;

void StartTraceLog(char const *perf_id)
{
    fprintf(stderr, "[TRACE] [%s] Start\n", perf_id);
}

void FinishTraceLog(char const *perf_id, std::chrono::nanoseconds duration)
{
    fprintf(stderr, "[TRACE] [%s] End, duration = %lldns\n", perf_id, static_cast<long long>(duration.count()));
}
}  // namespace

namespace taihe {
void StartTrace(char const *perf_id)
{
    StartTraceLog(perf_id);
    auto begin = std::chrono::steady_clock::now();
    ani_perf_trace_stack.emplace_back(perf_id, begin);
}

void FinishTrace()
{
    if (ani_perf_trace_stack.empty()) {
        return;
    }
    auto [perf_id, begin] = ani_perf_trace_stack.back();
    ani_perf_trace_stack.pop_back();
    auto end = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(end - begin);
    FinishTraceLog(perf_id, duration);
}
}  // namespace taihe
#endif

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

ani_env *get_env()
{
    ani_vm *vm = get_vm();
    if (vm == nullptr) {
        TH_ANI_LOG_ERROR("ANI VM is not set");
        return nullptr;
    }
    ani_env *env = nullptr;
    ani_status status = vm->GetEnv(ANI_VERSION_1, &env);
    if (status != ANI_OK) {
        TH_ANI_LOG_ERROR("Failed to get ANI environment, status: %d", status);
    }
    return env;
}

env_guard::env_guard()
{
    ani_vm *vm = get_vm();
    if (vm == nullptr) {
        TH_ANI_LOG_ERROR("ANI VM is not set");
        return;
    }
    is_temporary = vm->GetEnv(ANI_VERSION_1, &env) != ANI_OK;
    if (is_temporary) {
        ani_status status = vm->AttachCurrentThread(nullptr, ANI_VERSION_1, &env);
        if (status != ANI_OK) {
            TH_ANI_LOG_ERROR("Failed to attach current thread to ANI VM, status: %d", status);
        }
    }
}

env_guard::~env_guard()
{
    ani_vm *vm = get_vm();
    if (vm == nullptr) {
        TH_ANI_LOG_ERROR("ANI VM is not set");
        return;
    }
    if (is_temporary) {
        ani_status status = vm->DetachCurrentThread();
        if (status != ANI_OK) {
            TH_ANI_LOG_ERROR("Failed to detach current thread from ANI VM, status: %d", status);
        }
    }
}
}  // namespace taihe

namespace taihe {
static ani_error create_ani_error(ani_env *env, taihe::string_view msg)
{
    ani_class errCls;
    char const *className = "escompat.Error";
    if (ANI_OK != env->FindClass(className, &errCls)) {
        TH_ANI_LOG_ERROR("Class not found: %s", className);
        return nullptr;
    }

    ani_method errCtor;
    if (ANI_OK != env->Class_FindMethod(errCls, "<ctor>", "C{std.core.String}C{escompat.ErrorOptions}:", &errCtor)) {
        TH_ANI_LOG_ERROR("Constructor not found: %s", className);
        return nullptr;
    }

    ani_string errMsg {};
    if (ANI_OK != env->String_NewUTF8(msg.c_str(), msg.size(), &errMsg)) {
        TH_ANI_LOG_ERROR("Failed to create error message string");
        return nullptr;
    }

    ani_ref undefined;
    if (ANI_OK != env->GetUndefined(&undefined)) {
        TH_ANI_LOG_ERROR("Failed to get undefined value");
        return nullptr;
    }

    ani_error errObj;
    if (ANI_OK != env->Object_New(errCls, errCtor, reinterpret_cast<ani_object *>(&errObj), errMsg, undefined)) {
        TH_ANI_LOG_ERROR("Create Object Failed: %s", className);
        return nullptr;
    }
    return errObj;
}

static ani_error create_ani_business_error(ani_env *env, int32_t code, taihe::string_view msg)
{
    ani_class errCls;
    char const *className = "@ohos.base.BusinessError";
    if (ANI_OK != env->FindClass(className, &errCls)) {
        TH_ANI_LOG_ERROR("Class not found: %s", className);
        return nullptr;
    }

    ani_method errCtor;
    if (ANI_OK != env->Class_FindMethod(errCls, "<ctor>", "iC{escompat.Error}:", &errCtor)) {
        TH_ANI_LOG_ERROR("Constructor not found: %s", className);
        return nullptr;
    }

    ani_error errObj = create_ani_error(env, msg);
    ani_int errCode = static_cast<ani_int>(code);

    ani_error businessErrObj;
    if (ANI_OK != env->Object_New(errCls, errCtor, reinterpret_cast<ani_object *>(&businessErrObj), errCode, errObj)) {
        TH_ANI_LOG_ERROR("Create Object Failed: %s", className);
        return nullptr;
    }
    return businessErrObj;
}

static void set_ani_error(ani_env *env, taihe::string_view msg)
{
    ani_error errObj = create_ani_error(env, msg);
    TH_ANI_CHECKED_CALL(env, ThrowError, errObj);
}

static void set_ani_business_error(ani_env *env, int32_t code, taihe::string_view msg)
{
    ani_error businessErrObj = create_ani_business_error(env, code, msg);
    TH_ANI_CHECKED_CALL(env, ThrowError, businessErrObj);
}

static void reset_ani_error(ani_env *env)
{
    TH_ANI_CHECKED_CALL(env, ResetError);
}

static bool has_ani_error(ani_env *env)
{
    ani_boolean res;
    TH_ANI_CHECKED_CALL(env, ExistUnhandledError, &res);
    return res;
}

void set_error(taihe::string_view msg)
{
    env_guard guard;
    ani_env *env = guard.get_env();
    set_ani_error(env, msg);
}

void set_business_error(int32_t code, taihe::string_view msg)
{
    env_guard guard;
    ani_env *env = guard.get_env();
    set_ani_business_error(env, code, msg);
}

void reset_error()
{
    env_guard guard;
    ani_env *env = guard.get_env();
    reset_ani_error(env);
}

bool has_error()
{
    env_guard guard;
    ani_env *env = guard.get_env();
    return has_ani_error(env);
}
}  // namespace taihe

namespace taihe {
taihe::error from_ani_taihe_error(ani_env *env, ani_error errObj)
{
    ani_string errMsg {};
    TH_ANI_CHECKED_CALL(env, Object_GetPropertyByName_Ref, errObj, "message", reinterpret_cast<ani_ref *>(&errMsg));
    ani_size msgLength;
    TH_ANI_CHECKED_CALL(env, String_GetUTF8Size, errMsg, &msgLength);
    TString msgHandle;
    char *msgBuffer = tstr_initialize(&msgHandle, msgLength + 1);
    TH_ANI_CHECKED_CALL(env, String_GetUTF8, errMsg, msgBuffer, msgLength + 1, &msgLength);
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

ani_error into_ani_taihe_error(ani_env *env, taihe::error const &err)
{
    return create_ani_business_error(env, err.code(), err.message());
}

void throw_ani_taihe_error(ani_env *env, taihe::error const &err)
{
    ani_error errObj = into_ani_taihe_error(env, err);
    TH_ANI_CHECKED_CALL(env, ThrowError, errObj);
}

taihe::error catch_ani_taihe_error(ani_env *env)
{
    ani_error errObj;
    TH_ANI_CHECKED_CALL(env, GetUnhandledError, &errObj);
    TH_ANI_CHECKED_CALL(env, ResetError);
    return from_ani_taihe_error(env, errObj);
}
}  // namespace taihe
