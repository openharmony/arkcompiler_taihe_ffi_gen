/*
 * Copyright (c) 2026 Huawei Device Co., Ltd.
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

#ifndef TAIHE_ASYNC_ABI_H
#define TAIHE_ASYNC_ABI_H

#include <taihe/common.h>

union TAsyncHandlerStorage {
    void *pointer;
    char buffer[sizeof(void *)];
};

// Once-guard for result emplacement: atomically claimed at the start of
// emplace_result(). Prevents the result from being set more than once.
enum TAsyncContextResultGuard : uint8_t {
    TH_ASYNC_CONTEXT_RESULT_NONE = 0,
    TH_ASYNC_CONTEXT_RESULT_LOCKED = 1,
};

// Once-guard for handler registration: atomically claimed at the start of
// emplace_handler() / new_handler(). Prevents the handler from being set more than once.
enum TAsyncContextHandlerGuard : uint8_t {
    TH_ASYNC_CONTEXT_HANDLER_NONE = 0,
    TH_ASYNC_CONTEXT_HANDLER_LOCKED = 1,
};

// Rendezvous flags for the lock-free handshake between result emplacement and
// handler registration. Each side atomically sets its own bit and checks the
// other's: whichever side arrives second finds both bits set and dispatches the handler.
enum TAsyncHandshakeFlags : uint8_t {
    TH_ASYNC_HANDSHAKE_NONE = 0,
    TH_ASYNC_HANDSHAKE_RESULT_READY = 1 << 0,
    TH_ASYNC_HANDSHAKE_HANDLER_READY = 1 << 1,
};

struct TAsyncContext {
    uint32_t ref_count;
    uint8_t handler_guard;
    uint8_t result_guard;
    uint8_t handshake_flags;
    uint8_t reserved;

    void (*process_handler_ptr)(union TAsyncHandlerStorage *storage_ptr, void *result_ptr);
    void (*cleanup_handler_ptr)(union TAsyncHandlerStorage *storage_ptr);
    union TAsyncHandlerStorage storage;
    char buffer[];
};

struct TCompleter {
    struct TAsyncContext *m_ctx;
};

struct TFuture {
    struct TAsyncContext *m_ctx;
};

#endif  // TAIHE_ASYNC_ABI_H
