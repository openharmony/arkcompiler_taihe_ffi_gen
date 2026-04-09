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
    void *ptr;
    char buf[sizeof(void *) * 4];
};

enum TAsyncContextFlags : uint32_t {
    ASYNC_CONTEXT_NONE = 0,
    ASYNC_CONTEXT_RESULT_SET = 1 << 0,
    ASYNC_CONTEXT_HANDLER_SET = 1 << 1,
};

struct TAsyncContext {
    uint32_t ref_count;
    uint32_t flags;

    union TAsyncHandlerStorage storage;
    void (*process_handler_ptr)(union TAsyncHandlerStorage storage, void *resptr);
    void (*cleanup_handler_ptr)(union TAsyncHandlerStorage storage);

    char buffer[];
};

struct TCompleter {
    struct TAsyncContext *m_ctx;
};

struct TFuture {
    struct TAsyncContext *m_ctx;
};

#endif  // TAIHE_ASYNC_ABI_H
