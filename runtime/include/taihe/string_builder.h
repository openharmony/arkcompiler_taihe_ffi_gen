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
#if TSTR_ENABLE_STRING_SSO
    union {
        struct {
#endif
            void *buffer;
            struct TStringInternalControlBlock *cb;
#if TSTR_ENABLE_STRING_SSO
        };

        char small_utf8[TSTR_SMALL_UTF8_CAPACITY];
        uint16_t small_utf16[TSTR_SMALL_UTF16_CAPACITY];
    };
#endif
};

// Returns the TStringBuilder encoding.
TH_INLINE uint32_t tstr_builder_encoding(struct TStringBuilder builder)
{
    return builder.flags & TSTRING_ENCODING_MASK;
}

// Returns the TStringBuilder storage type.
TH_INLINE uint32_t tstr_builder_mode(struct TStringBuilder builder)
{
    return builder.flags & TSTRING_STORAGE_MASK;
}

// Check if the TStringBuilder is valid.
TH_INLINE uint32_t tstr_builder_valid(struct TStringBuilder builder)
{
    return tstr_builder_mode(builder) != TSTRING_STORAGE_INVALID;
}

// Sets the TStringBuilder mode to invalid.
TH_INLINE void tstr_builder_set_invalid(struct TStringBuilder *builder_ptr)
{
    builder_ptr->flags = (builder_ptr->flags & ~TSTRING_STORAGE_MASK) | TSTRING_STORAGE_INVALID;
}

// Returns the UTF8 buffer.
TH_INLINE char const *tstr_builder_buf_utf8(struct TStringBuilder const *bref)
{
#if TSTR_ENABLE_STRING_SSO
    return tstr_builder_mode(*bref) == TSTRING_STORAGE_SMALL ? bref->small_utf8 : (char const *)bref->buffer;
#else
    return (char const *)bref->buffer;
#endif
}

// Returns the UTF16 buffer.
TH_INLINE uint16_t const *tstr_builder_buf_utf16(struct TStringBuilder const *bref)
{
#if TSTR_ENABLE_STRING_SSO
    return tstr_builder_mode(*bref) == TSTRING_STORAGE_SMALL ? bref->small_utf16 : (uint16_t const *)bref->buffer;
#else
    return (uint16_t const *)bref->buffer;
#endif
}

// Returns the mutable UTF8 buffer.
TH_INLINE char *tstr_builder_mut_buf_utf8(struct TStringBuilder *bref)
{
#if TSTR_ENABLE_STRING_SSO
    return tstr_builder_mode(*bref) == TSTRING_STORAGE_SMALL ? bref->small_utf8 : (char *)bref->buffer;
#else
    return (char *)bref->buffer;
#endif
}

// Returns the mutable UTF16 buffer.
TH_INLINE uint16_t *tstr_builder_mut_buf_utf16(struct TStringBuilder *bref)
{
#if TSTR_ENABLE_STRING_SSO
    return tstr_builder_mode(*bref) == TSTRING_STORAGE_SMALL ? bref->small_utf16 : (uint16_t *)bref->buffer;
#else
    return (uint16_t *)bref->buffer;
#endif
}

// Returns the UTF8 capacity in bytes.
TH_INLINE size_t tstr_builder_cap_utf8(struct TStringBuilder builder)
{
    return builder.byte_capacity / sizeof(char);
}

// Returns the UTF16 capacity in code units.
TH_INLINE size_t tstr_builder_cap_utf16(struct TStringBuilder builder)
{
    return builder.byte_capacity / sizeof(uint16_t);
}

TH_EXPORT struct TStringBuilder tstr_builder_new_utf8(size_t capacity);
TH_EXPORT struct TStringBuilder tstr_builder_new_utf16(size_t capacity);
TH_EXPORT bool tstr_builder_reallocate_utf8(struct TStringBuilder *builder_ptr, size_t capacity, size_t length);
TH_EXPORT bool tstr_builder_reallocate_utf16(struct TStringBuilder *builder_ptr, size_t capacity, size_t length);
TH_EXPORT struct TString tstr_builder_finish_utf8(struct TStringBuilder builder, size_t length);
TH_EXPORT struct TString tstr_builder_finish_utf16(struct TStringBuilder builder, size_t length);
TH_EXPORT void tstr_builder_drop(struct TStringBuilder builder);

#endif  // TAIHE_STRING_BUILDER_H
