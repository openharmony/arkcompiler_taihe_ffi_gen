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

#ifndef TAIHE_RUNTIME_ANI_HPP
#define TAIHE_RUNTIME_ANI_HPP

#if __has_include(<ani.h>)
#include <ani.h>
#elif __has_include(<ani/ani.h>)
#include <ani/ani.h>
#else
#error "ani.h not found. Please ensure the Ani SDK is correctly installed."
#endif

#ifndef TH_ANI_ENABLE_PERF_TRACE
#define TH_ANI_PERF_TRACE_BEGIN(perf_id)
#define TH_ANI_PERF_TRACE_END()
#elif __has_include(<hitrace/trace.h>)
#include <hitrace/trace.h>
#define TH_ANI_PERF_TRACE_BEGIN(perf_id) OH_HiTrace_StartTraceEx(HITRACE_LEVEL_DEBUG, perf_id, "")
#define TH_ANI_PERF_TRACE_END() OH_HiTrace_FinishTraceEx(HITRACE_LEVEL_DEBUG)
#elif __has_include("hitrace_meter.h")
#include "hitrace_meter.h"
#define TH_ANI_PERF_TRACE_BEGIN(perf_id) StartTraceEx(HITRACE_LEVEL_DEBUG, HITRACE_TAG_OHOS, perf_id, "")
#define TH_ANI_PERF_TRACE_END() FinishTraceEx(HITRACE_LEVEL_DEBUG, HITRACE_TAG_OHOS)
#else
#define TH_ANI_USE_LOCAL_TRACE
#define TH_ANI_PERF_TRACE_BEGIN(perf_id) ::taihe::StartTrace(perf_id)
#define TH_ANI_PERF_TRACE_END() ::taihe::FinishTrace()
#endif

#include <taihe/object.hpp>
#include <taihe/string.hpp>
#include <taihe/expected.hpp>

#ifdef TH_ANI_USE_LOCAL_TRACE
namespace taihe {
void StartTrace(char const *perf_id);
void FinishTrace();
}  // namespace taihe
#endif

namespace taihe {
// VM and Environment related functions

void set_vm(ani_vm *vm);
ani_vm *get_vm();

inline ani_env *get_env()
{
    ani_env *env = nullptr;
    get_vm()->GetEnv(ANI_VERSION_1, &env);
    return env;
}

class env_guard {
    ani_env *env = nullptr;
    bool is_temporary;

public:
    env_guard()
    {
        is_temporary = get_vm()->GetEnv(ANI_VERSION_1, &env) != ANI_OK;
        if (is_temporary) {
            get_vm()->AttachCurrentThread(nullptr, ANI_VERSION_1, &env);
        }
    }

    ~env_guard()
    {
        if (is_temporary) {
            get_vm()->DetachCurrentThread();
        }
    }

    env_guard(env_guard const &) = delete;
    env_guard &operator=(env_guard const &) = delete;
    env_guard(env_guard &&) = delete;
    env_guard &operator=(env_guard &&) = delete;

    ani_env *get_env()
    {
        return env;
    }
};
}  // namespace taihe

namespace taihe {
// Error handling functions

void set_error(taihe::string_view msg);
void set_business_error(int32_t err_code, taihe::string_view msg);
void reset_error();
bool has_error();
}  // namespace taihe

namespace taihe {
// Internal Error handling functions

taihe::error catch_ani_taihe_error(ani_env *env);
taihe::error from_ani_taihe_error(ani_env *env, ani_error err);
ani_error into_ani_taihe_error(ani_env *env, taihe::error const &err);
void throw_ani_taihe_error(ani_env *env, taihe::error const &err);
}  // namespace taihe

#endif  // TAIHE_RUNTIME_ANI_HPP
