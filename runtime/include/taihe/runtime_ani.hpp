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

#if __has_include("hilog/log.h") && defined(TH_ANI_USE_HILOG)
#ifdef HIVIEWDFX_HILOG_C_H  // SDK scenario
#define OH_LOG_Print HiLogPrint
#endif
#include "hilog/log.h"
#define TH_ANI_LOG_DOMAIN 0x3200
#define TH_ANI_LOG_TAG "Taihe"
#define TH_ANI_LOG_DEBUG(fmt, ...) \
    (void)OH_LOG_Print(LOG_APP, LOG_DEBUG, TH_ANI_LOG_DOMAIN, TH_ANI_LOG_TAG, fmt, ##__VA_ARGS__)
#define TH_ANI_LOG_INFO(fmt, ...) \
    (void)OH_LOG_Print(LOG_APP, LOG_INFO, TH_ANI_LOG_DOMAIN, TH_ANI_LOG_TAG, fmt, ##__VA_ARGS__)
#define TH_ANI_LOG_WARN(fmt, ...) \
    (void)OH_LOG_Print(LOG_APP, LOG_WARN, TH_ANI_LOG_DOMAIN, TH_ANI_LOG_TAG, fmt, ##__VA_ARGS__)
#define TH_ANI_LOG_ERROR(fmt, ...) \
    (void)OH_LOG_Print(LOG_APP, LOG_ERROR, TH_ANI_LOG_DOMAIN, TH_ANI_LOG_TAG, fmt, ##__VA_ARGS__)
#define TH_ANI_LOG_FATAL(fmt, ...) \
    (void)OH_LOG_Print(LOG_APP, LOG_FATAL, TH_ANI_LOG_DOMAIN, TH_ANI_LOG_TAG, fmt, ##__VA_ARGS__)
#else
#define TH_ANI_LOG_LEVEL_DEBUG 3
#define TH_ANI_LOG_LEVEL_INFO 4
#define TH_ANI_LOG_LEVEL_WARN 5
#define TH_ANI_LOG_LEVEL_ERROR 6
#define TH_ANI_LOG_LEVEL_FATAL 7
#ifndef TH_ANI_LOG_LEVEL
#define TH_ANI_LOG_LEVEL TH_ANI_LOG_LEVEL_DEBUG
#endif
#if TH_ANI_LOG_LEVEL <= TH_ANI_LOG_LEVEL_DEBUG
#define TH_ANI_LOG_DEBUG(fmt, ...) (void)fprintf(stderr, "[DEBUG] " fmt "\n", ##__VA_ARGS__)
#else
#define TH_ANI_LOG_DEBUG(fmt, ...)
#endif
#if TH_ANI_LOG_LEVEL <= TH_ANI_LOG_LEVEL_INFO
#define TH_ANI_LOG_INFO(fmt, ...) (void)fprintf(stderr, "[INFO] " fmt "\n", ##__VA_ARGS__)
#else
#define TH_ANI_LOG_INFO(fmt, ...)
#endif
#if TH_ANI_LOG_LEVEL <= TH_ANI_LOG_LEVEL_WARN
#define TH_ANI_LOG_WARN(fmt, ...) (void)fprintf(stderr, "[WARN] " fmt "\n", ##__VA_ARGS__)
#else
#define TH_ANI_LOG_WARN(fmt, ...)
#endif
#if TH_ANI_LOG_LEVEL <= TH_ANI_LOG_LEVEL_ERROR
#define TH_ANI_LOG_ERROR(fmt, ...) (void)fprintf(stderr, "[ERROR] " fmt "\n", ##__VA_ARGS__)
#else
#define TH_ANI_LOG_ERROR(fmt, ...)
#endif
#if TH_ANI_LOG_LEVEL <= TH_ANI_LOG_LEVEL_FATAL
#define TH_ANI_LOG_FATAL(fmt, ...) (void)fprintf(stderr, "[FATAL] " fmt "\n", ##__VA_ARGS__)
#else
#define TH_ANI_LOG_FATAL(fmt, ...)
#endif
#endif

#define TH_ANI_ASSERT(cond, msg, ...)                                  \
    do {                                                               \
        if (!(cond)) {                                                 \
            TH_ANI_LOG_FATAL("Assertion failed: " msg, ##__VA_ARGS__); \
            std::abort();                                              \
        }                                                              \
    } while (0)

#ifndef TH_ANI_ENABLE_CHECKED_CALL
#define TH_ANI_CHECKED_CALL(env, func, ...) env->func(__VA_ARGS__)
#else
#define TH_ANI_CHECKED_CALL(env, func, ...)                                                  \
    do {                                                                                     \
        ani_status status = env->func(__VA_ARGS__);                                          \
        TH_ANI_ASSERT(status == ANI_OK, "ANI call " #func " failed with status %d", status); \
    } while (0)
#endif

#ifndef TH_ANI_ENABLE_PERF_TRACE
#define TH_ANI_PERF_TRACE_BEGIN(perf_id)
#define TH_ANI_PERF_TRACE_END()
#elif __has_include(<hitrace/trace.h>)  // Third-party scenario
#include <hitrace/trace.h>
#define TH_ANI_PERF_TRACE_BEGIN(perf_id) OH_HiTrace_StartTraceEx(HITRACE_LEVEL_DEBUG, perf_id, "")
#define TH_ANI_PERF_TRACE_END() OH_HiTrace_FinishTraceEx(HITRACE_LEVEL_DEBUG)
#elif __has_include("hitrace_meter.h")  // SDK scenario
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

class env_guard {
    ani_env *env = nullptr;
    bool is_temporary;

public:
    env_guard()
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

    ~env_guard()
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
