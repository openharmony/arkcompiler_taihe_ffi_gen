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

#ifndef TAIHE_STRING_BUILDER_H
#define TAIHE_STRING_BUILDER_H

#include <taihe/string.abi.h>

#ifndef TSTR_BUILDER_USE_REALLOC
#define TSTR_BUILDER_USE_REALLOC 0
#endif

struct TStringBuilder {
    uint32_t flags;
    uint32_t byte_capacity;
    void *buffer;
    struct TStringInternalControlBlock *cb;
};

// A TStringBuilder returned by a constructor is a holder, including when
// invalid, and must be consumed exactly once by a matching finish function or
// by tstr_builder_drop. Its buffers are borrowed and remain valid only until
// reallocation or consumption.

TH_INLINE uint32_t tstr_builder_encoding(struct TStringBuilder builder)
{
    return builder.flags & TSTRING_ENCODING_MASK;
}

TH_INLINE void const *tstr_builder_buffer(struct TStringBuilder builder)
{
    return builder.buffer;
}

TH_INLINE char const *tstr_builder_buf_utf8(struct TStringBuilder builder)
{
    return (char const *)tstr_builder_buffer(builder);
}

TH_INLINE uint16_t const *tstr_builder_buf_utf16(struct TStringBuilder builder)
{
    return (uint16_t const *)tstr_builder_buffer(builder);
}

TH_INLINE void *tstr_builder_mut_buffer(struct TStringBuilder builder)
{
    return builder.buffer;
}

TH_INLINE char *tstr_builder_mut_buf_utf8(struct TStringBuilder builder)
{
    return (char *)tstr_builder_mut_buffer(builder);
}

TH_INLINE uint16_t *tstr_builder_mut_buf_utf16(struct TStringBuilder builder)
{
    return (uint16_t *)tstr_builder_mut_buffer(builder);
}

TH_INLINE size_t tstr_builder_byte_capacity(struct TStringBuilder builder)
{
    return builder.byte_capacity;
}

TH_INLINE size_t tstr_builder_cap_utf8(struct TStringBuilder builder)
{
    return tstr_builder_byte_capacity(builder) / sizeof(char);
}

TH_INLINE size_t tstr_builder_cap_utf16(struct TStringBuilder builder)
{
    return tstr_builder_byte_capacity(builder) / sizeof(uint16_t);
}

TH_EXPORT struct TStringBuilder tstr_builder_new_invalid();

// Creates a UTF8 builder holder.
//
// # Arguments
// - `capacity`: The buffer capacity in bytes.
//
// # Returns
// - A builder holder, or an invalid builder holder if allocation fails.
TH_EXPORT struct TStringBuilder tstr_builder_new_utf8(size_t capacity);

// Creates a UTF16 builder holder.
//
// # Arguments
// - `capacity`: The buffer capacity in UTF16 code units.
//
// # Returns
// - A builder holder, or an invalid builder holder if allocation fails.
TH_EXPORT struct TStringBuilder tstr_builder_new_utf16(size_t capacity);

// Replaces a UTF8 builder holder with one of the requested capacity.
//
// # Arguments
// - `builder_ptr`: Pointer to a valid UTF8 builder holder.
// - `capacity`: The new capacity in bytes.
// - `length`: The initialized prefix length in bytes. At most the old and new
//   capacities are preserved.
//
// # Returns
// - True on success. On failure, the original holder remains unchanged.
//
// # Notes
// - All previously obtained buffer pointers are invalid after success.
TH_EXPORT bool tstr_builder_reallocate_utf8(struct TStringBuilder *builder_ptr, size_t capacity, size_t length);

// Replaces a UTF16 builder holder with one of the requested capacity.
//
// # Arguments
// - `builder_ptr`: Pointer to a valid UTF16 builder holder.
// - `capacity`: The new capacity in UTF16 code units.
// - `length`: The initialized prefix length in UTF16 code units. At most the
//   old and new capacities are preserved.
//
// # Returns
// - True on success. On failure, the original holder remains unchanged.
//
// # Notes
// - All previously obtained buffer pointers are invalid after success.
TH_EXPORT bool tstr_builder_reallocate_utf16(struct TStringBuilder *builder_ptr, size_t capacity, size_t length);

// Consumes a UTF8 builder holder and returns its initialized prefix as a holder.
//
// # Arguments
// - `builder`: The UTF8 builder holder to consume.
// - `length`: The initialized prefix length in bytes.
//
// # Returns
// - A UTF8 holder, or an invalid holder if the builder or length is invalid.
//
// # Notes
// - The builder is consumed on both success and failure.
TH_EXPORT struct TString tstr_builder_finish_utf8(struct TStringBuilder builder, size_t length);

// Consumes a UTF16 builder holder and returns its initialized prefix as a holder.
//
// # Arguments
// - `builder`: The UTF16 builder holder to consume.
// - `length`: The initialized prefix length in UTF16 code units.
//
// # Returns
// - A UTF16 holder, or an invalid holder if the builder or length is invalid.
//
// # Notes
// - The builder is consumed on both success and failure.
TH_EXPORT struct TString tstr_builder_finish_utf16(struct TStringBuilder builder, size_t length);

// Fulfills the drop responsibility of one builder holder.
TH_EXPORT void tstr_builder_drop(struct TStringBuilder builder);

#endif  // TAIHE_STRING_BUILDER_H
