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

#include <taihe/shared_array.abi.h>

#include <cstddef>
#include <cstdlib>

TH_INLINE void tarr_set_data(TSharedArray *tarr_ptr, void *data)
{
    tarr_ptr->data = data;
}

TH_INLINE void tarr_set_byte_length(TSharedArray *tarr_ptr, size_t byte_length)
{
    tarr_ptr->byte_length = byte_length;
}

TH_INLINE uint32_t tarr_mode(TSharedArray tarr)
{
    return tarr.flags & TSHARED_ARRAY_STORAGE_MASK;
}

TH_INLINE uint32_t tarr_is_valid(TSharedArray tarr)
{
    return tarr_mode(tarr) != TSHARED_ARRAY_STORAGE_INVALID;
}

TSharedArray tarr_new_invalid()
{
    TSharedArray tarr;
    tarr.flags = TSHARED_ARRAY_STORAGE_INVALID;
    tarr_set_byte_length(&tarr, 0);
    tarr_set_data(&tarr, nullptr);
    return tarr;
}

TSharedArray tarr_new_static(void *data, size_t byte_length)
{
    TSharedArray tarr;
    tarr.flags = TSHARED_ARRAY_STORAGE_STATIC;
    tarr_set_data(&tarr, data);
    tarr_set_byte_length(&tarr, byte_length);
    return tarr;
}

TSharedArrayInternalControlBlock *tarr_internal_control_block_new(size_t bytes)
{
    size_t required = sizeof(TSharedArrayInternalControlBlock) + bytes;
    auto cb = reinterpret_cast<TSharedArrayInternalControlBlock *>(malloc(required));
    if (!cb) {
        return nullptr;
    }
    tref_init(&cb->ref_count, 1);
    return cb;
}

TSharedArray tarr_new_internal_raw(void *data, size_t byte_length,
                                   TSharedArrayInternalControlBlock *internal_cb TH_NONNULL)
{
    TSharedArray tarr;
    tarr.flags = TSHARED_ARRAY_STORAGE_INTERNAL;
    tarr_set_data(&tarr, data);
    tarr_set_byte_length(&tarr, byte_length);
    tarr.internal_cb = internal_cb;
    return tarr;
}

TSharedArray tarr_new_internal(size_t byte_length)
{
    auto cb = tarr_internal_control_block_new(byte_length);
    if (!cb) {
        return tarr_new_invalid();
    }
    void *buf = cb + 1;
    return tarr_new_internal_raw(buf, byte_length, cb);
}

void tarr_global_context_release(TSharedArrayGlobalRefContext ctx)
{
    ctx.release(ctx.ref);
}

TSharedArrayAcquiredControlBlock *tarr_acquired_control_block_new(TSharedArrayGlobalRefContext ctx)
{
    size_t required = sizeof(TSharedArrayAcquiredControlBlock);
    auto cb = reinterpret_cast<TSharedArrayAcquiredControlBlock *>(malloc(required));
    if (!cb) {
        tarr_global_context_release(ctx);
        return nullptr;
    }
    cb->global_ctx = ctx;
    tref_init(&cb->ref_count, 1);
    return cb;
}

TSharedArray tarr_new_acquired_raw(void *data, size_t byte_length,
                                   TSharedArrayAcquiredControlBlock *acquired_cb TH_NONNULL)
{
    TSharedArray tarr;
    tarr.flags = TSHARED_ARRAY_STORAGE_ACQUIRED;
    tarr_set_data(&tarr, data);
    tarr_set_byte_length(&tarr, byte_length);
    tarr.acquired_cb = acquired_cb;
    return tarr;
}

TSharedArray tarr_new_acquired(void *data, size_t byte_length, TSharedArrayGlobalRefContext ctx)
{
    auto cb = tarr_acquired_control_block_new(ctx);
    if (!cb) {
        return tarr_new_invalid();
    }
    return tarr_new_acquired_raw(data, byte_length, cb);
}

void tarr_acquire_cache_init(struct TSharedArrayAcquireCache *cache TH_NONNULL, struct TSharedArrayLocalRefContext ctx)
{
    cache->acquired_cb = nullptr;
    cache->local_ctx = ctx;
}

TSharedArray tarr_new_acquirable_borrowed(void *data, size_t byte_length, TSharedArrayAcquireCache *cache TH_NONNULL,
                                          TSharedArrayLocalRefContext ctx)
{
    TSharedArray tarr;
    tarr.flags = TSHARED_ARRAY_STORAGE_ACQUIRABLE_BORROWED;
    tarr_set_data(&tarr, data);
    tarr_set_byte_length(&tarr, byte_length);
    tarr.acquire_cache = cache;
    tarr_acquire_cache_init(cache, ctx);
    return tarr;
}

TSharedArray tarr_subview_raw(TSharedArray tarr, size_t byte_offset, size_t byte_length)
{
    tarr_set_data(&tarr, reinterpret_cast<std::byte *>(tarr_data(tarr)) + byte_offset);
    tarr_set_byte_length(&tarr, byte_length);
    return tarr;
}

TSharedArray tarr_subview(TSharedArray tarr, size_t byte_offset, size_t byte_length)
{
    if (!tarr_is_valid(tarr)) {
        return tarr_new_invalid();
    }
    size_t byte_original = tarr_byte_length(tarr);
    if (byte_offset > byte_original) {
        return tarr_new_invalid();
    }
    size_t byte_remaining = byte_original - byte_offset;
    if (byte_length > byte_remaining) {
        byte_length = byte_remaining;
    }
    return tarr_subview_raw(tarr, byte_offset, byte_length);
}

TSharedArrayGlobalRefContext tarr_local_context_acquire(TSharedArrayLocalRefContext ctx)
{
    return ctx.acquire(ctx.ref);
}

TSharedArray tarr_acquire_cache_get_relative(TSharedArrayAcquireCache *cache TH_NONNULL, void *data, size_t byte_length)
{
    if (cache->acquired_cb == nullptr) {
        TSharedArrayGlobalRefContext ctx = tarr_local_context_acquire(cache->local_ctx);
        cache->acquired_cb = tarr_acquired_control_block_new(ctx);
        if (cache->acquired_cb == nullptr) {
            return tarr_new_invalid();
        }
    }
    return tarr_new_acquired_raw(data, byte_length, cache->acquired_cb);
}

TSharedArrayInternalControlBlock *tarr_internal_control_block_dup(TSharedArrayInternalControlBlock *cb TH_NONNULL)
{
    tref_inc(&cb->ref_count);
    return cb;
}

TSharedArrayAcquiredControlBlock *tarr_acquired_control_block_dup(TSharedArrayAcquiredControlBlock *cb TH_NONNULL)
{
    tref_inc(&cb->ref_count);
    return cb;
}

TSharedArray tarr_dup(TSharedArray tarr)
{
    uint32_t mode = tarr_mode(tarr);
    if (mode == TSHARED_ARRAY_STORAGE_STATIC) {
        return tarr;
    }
    if (mode == TSHARED_ARRAY_STORAGE_INTERNAL) {
        return tarr_new_internal_raw(tarr_data(tarr), tarr_byte_length(tarr),
                                     tarr_internal_control_block_dup(tarr.internal_cb));
    }
    if (mode == TSHARED_ARRAY_STORAGE_ACQUIRED) {
        return tarr_new_acquired_raw(tarr_data(tarr), tarr_byte_length(tarr),
                                     tarr_acquired_control_block_dup(tarr.acquired_cb));
    }
    if (mode == TSHARED_ARRAY_STORAGE_ACQUIRABLE_BORROWED) {
        return tarr_dup(tarr_acquire_cache_get_relative(tarr.acquire_cache, tarr_data(tarr), tarr_byte_length(tarr)));
    }
    return tarr_new_invalid();
}

void tarr_internal_control_block_drop(TSharedArrayInternalControlBlock *cb TH_NONNULL)
{
    if (tref_dec(&cb->ref_count)) {
        free(cb);
    }
}

void tarr_acquired_control_block_drop(TSharedArrayAcquiredControlBlock *cb TH_NONNULL)
{
    if (tref_dec(&cb->ref_count)) {
        tarr_global_context_release(cb->global_ctx);
        free(cb);
    }
}

void tarr_drop(TSharedArray tarr)
{
    uint32_t mode = tarr_mode(tarr);
    if (mode == TSHARED_ARRAY_STORAGE_INTERNAL) {
        tarr_internal_control_block_drop(tarr.internal_cb);
    }
    if (mode == TSHARED_ARRAY_STORAGE_ACQUIRED) {
        tarr_acquired_control_block_drop(tarr.acquired_cb);
    }
}

void tarr_acquire_cache_drop(TSharedArrayAcquireCache const *cache TH_NONNULL)
{
    if (cache->acquired_cb != nullptr) {
        tarr_acquired_control_block_drop(cache->acquired_cb);
    }
}
