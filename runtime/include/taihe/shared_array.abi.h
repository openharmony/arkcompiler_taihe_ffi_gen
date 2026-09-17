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

#ifndef TAIHE_SHARED_ARRAY_ABI_H
#define TAIHE_SHARED_ARRAY_ABI_H

#include <taihe/common.h>

#include <stddef.h>
#include <stdint.h>

enum TSharedArrayFlags {
    TSHARED_ARRAY_STORAGE_MASK = 0xFFFF,
    TSHARED_ARRAY_STORAGE_INVALID = 0u,
    TSHARED_ARRAY_STORAGE_STATIC = 1u,
    TSHARED_ARRAY_STORAGE_INTERNAL = 2u,
    TSHARED_ARRAY_STORAGE_ACQUIRED = 4u,
    TSHARED_ARRAY_STORAGE_ACQUIRABLE_BORROWED = 8u,
};

// An acquired reference that keeps an external buffer alive. Ownership of the
// reference is transferred with this structure and released at most once.
struct TSharedArrayGlobalRefContext {
    void *ref;
    void (*release)(void *);
};

// A local reference that can be acquired to produce an independently owned
// global reference. Calling acquire does not transfer ownership of the local
// reference itself.
struct TSharedArrayLocalRefContext {
    void *ref;
    struct TSharedArrayGlobalRefContext (*acquire)(void *);
};

struct TSharedArrayInternalControlBlock {
    TRefCount ref_count;
};

struct TSharedArrayAcquiredControlBlock {
    TRefCount ref_count;
    struct TSharedArrayGlobalRefContext global_ctx;
};

// Lazily caches one acquired control block. The cache is initialized exactly
// once by tarr_new_acquirable_borrowed and must later be passed exactly once to
// tarr_acquire_cache_drop.
struct TSharedArrayAcquireCache {
    struct TSharedArrayAcquiredControlBlock *acquired_cb;
    struct TSharedArrayLocalRefContext local_ctx;
};

struct TSharedArray {
    uint32_t flags;
    uint32_t byte_length;
    void *data;

    union {
        struct TSharedArrayInternalControlBlock *internal_cb;
        struct TSharedArrayAcquiredControlBlock *acquired_cb;
        struct TSharedArrayAcquireCache *acquire_cache;
    };
};

TH_INLINE void *tarr_data(struct TSharedArray tarr)
{
    return tarr.data;
}

TH_INLINE size_t tarr_byte_length(struct TSharedArray tarr)
{
    return tarr.byte_length;
}

TH_INLINE uint32_t tarr_is_empty(struct TSharedArray tarr)
{
    return tarr.byte_length == 0;
}

// API lifetime semantics:
// - A holder is an independent value and must be passed exactly once to
//   tarr_drop, including when it is invalid.
// - A borrowed view has no drop responsibility and must not outlive the holder
//   or static buffer on which it depends.

TH_EXPORT struct TSharedArray tarr_new_invalid();

// Creates a holder with an uninitialized internal buffer.
TH_EXPORT struct TSharedArray tarr_new_internal(size_t byte_length);

// Creates a holder from an acquired external buffer and consumes `ctx` on both
// success and failure. The buffer must remain valid until ctx.release is
// called.
TH_EXPORT struct TSharedArray tarr_new_acquired(void *data, size_t byte_length,
                                                struct TSharedArrayGlobalRefContext ctx);

// Creates a borrowed view whose first duplication lazily acquires a global
// reference. The cache is shared by derived views, must outlive them, and must
// later be passed exactly once to tarr_acquire_cache_drop.
TH_EXPORT struct TSharedArray tarr_new_acquirable_borrowed(void *data, size_t byte_length,
                                                           struct TSharedArrayAcquireCache *cache,
                                                           struct TSharedArrayLocalRefContext ctx);

// Creates a static value that may be treated as either a holder or a borrowed
// view. Passing it to tarr_drop is valid but unnecessary.
TH_EXPORT struct TSharedArray tarr_new_static(void *data, size_t byte_length);

// Creates a borrowed view into the selected byte range. The result must not
// outlive the source holder or static buffer and must not be passed to
// tarr_drop.
TH_EXPORT struct TSharedArray tarr_subview(struct TSharedArray tarr, size_t byte_offset, size_t byte_length);

// Creates an independent holder from a shared array value.
TH_EXPORT struct TSharedArray tarr_dup(struct TSharedArray tarr);

// Fulfills the drop responsibility of one holder. Borrowed views must not be
// passed to this function.
TH_EXPORT void tarr_drop(struct TSharedArray tarr);

// Releases the cache's acquired reference, if acquisition occurred.
TH_EXPORT void tarr_acquire_cache_drop(struct TSharedArrayAcquireCache const *cache);

#endif  // TAIHE_SHARED_ARRAY_ABI_H
