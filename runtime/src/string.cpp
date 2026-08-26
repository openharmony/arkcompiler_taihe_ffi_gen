/*
 * Copyright (c) 2025-2026 Huawei Device Co., Ltd.
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

#include <taihe/string.abi.h>
#include <taihe/string_builder.h>

#include <algorithm>
#include <cstddef>
#include <cstdint>

// Sets the UTF8 capacity in bytes.
TH_INLINE void tstr_builder_set_cap_utf8(struct TStringBuilder *builder_ptr, size_t cap)
{
    builder_ptr->byte_capacity = cap * sizeof(char);
}

// Sets the UTF16 capacity in code units.
TH_INLINE void tstr_builder_set_cap_utf16(struct TStringBuilder *builder_ptr, size_t cap)
{
    builder_ptr->byte_capacity = cap * sizeof(uint16_t);
}

// Sets the UTF8 buffer.
TH_INLINE void tstr_builder_set_buf_utf8(struct TStringBuilder *builder_ptr, char *buf)
{
    builder_ptr->buffer = buf;
}

// Sets the UTF16 buffer.
TH_INLINE void tstr_builder_set_buf_utf16(struct TStringBuilder *builder_ptr, uint16_t *buf)
{
    builder_ptr->buffer = buf;
}

// Sets the UTF8 length in bytes.
TH_INLINE void tstr_set_len_utf8(struct TString *tstr_ptr, size_t len)
{
    tstr_ptr->byte_length = len * sizeof(char);
}

// Sets the UTF16 length in code units.
TH_INLINE void tstr_set_len_utf16(struct TString *tstr_ptr, size_t len)
{
    tstr_ptr->byte_length = len * sizeof(uint16_t);
}

// Sets the UTF8 buffer.
TH_INLINE void tstr_set_buf_utf8(struct TString *tstr_ptr, char const *buf)
{
    tstr_ptr->data = buf;
}

// Sets the UTF16 buffer.
TH_INLINE void tstr_set_buf_utf16(struct TString *tstr_ptr, uint16_t const *buf)
{
    tstr_ptr->data = buf;
}

TStringBuilder tstr_builder_new_invalid(uint32_t encoding)
{
    TStringBuilder builder;
    builder.flags = TSTRING_STORAGE_INVALID | (encoding & TSTRING_ENCODING_MASK);
    builder.byte_capacity = 0;
    builder.buffer = nullptr;
    return builder;
}

TStringBuilder tstr_builder_new_invalid_utf8()
{
    return tstr_builder_new_invalid(TSTRING_ENCODING_UTF8);
}

TStringBuilder tstr_builder_new_invalid_utf16()
{
    return tstr_builder_new_invalid(TSTRING_ENCODING_UTF16);
}

TString tstr_new_invalid(uint32_t encoding)
{
    TString tstr;
    tstr.flags = TSTRING_STORAGE_INVALID | (encoding & TSTRING_ENCODING_MASK);
    tstr.byte_length = 0;
    tstr.data = nullptr;
    return tstr;
}

TString tstr_new_invalid_utf8()
{
    return tstr_new_invalid(TSTRING_ENCODING_UTF8);
}

TString tstr_new_invalid_utf16()
{
    return tstr_new_invalid(TSTRING_ENCODING_UTF16);
}

#if TSTR_ENABLE_STRING_SSO
TStringBuilder tstr_builder_new_small_utf8(size_t capacity)
{
    if (capacity > TSTR_SMALL_UTF8_MAX_LENGTH) [[unlikely]] {
        return tstr_builder_new_invalid_utf8();
    }

    TStringBuilder builder;
    builder.flags = TSTRING_STORAGE_SMALL | TSTRING_ENCODING_UTF8;
    tstr_builder_set_cap_utf8(&builder, capacity);
    return builder;
}

TStringBuilder tstr_builder_new_small_utf16(size_t capacity)
{
    if (capacity > TSTR_SMALL_UTF16_MAX_LENGTH) [[unlikely]] {
        return tstr_builder_new_invalid_utf16();
    }

    TStringBuilder builder;
    builder.flags = TSTRING_STORAGE_SMALL | TSTRING_ENCODING_UTF16;
    tstr_builder_set_cap_utf16(&builder, capacity);
    return builder;
}
#endif

TStringBuilder tstr_builder_new_utf8(size_t capacity)
{
#if TSTR_ENABLE_STRING_SSO
    if (capacity <= TSTR_SMALL_UTF8_MAX_LENGTH) {
        return tstr_builder_new_small_utf8(capacity);
    }
#endif

    size_t bytes = sizeof(TStringInternalControlBlock) + (capacity + 1) * sizeof(char);
    auto cb = reinterpret_cast<TStringInternalControlBlock *>(malloc(bytes));
    if (!cb) {
        return tstr_builder_new_invalid_utf8();
    }
    char *buffer = reinterpret_cast<char *>(cb + 1);
    TStringBuilder builder;
    builder.flags = TSTRING_STORAGE_INTERNAL | TSTRING_ENCODING_UTF8;
    tstr_builder_set_buf_utf8(&builder, buffer);
    tstr_builder_set_cap_utf8(&builder, capacity);
    builder.cb = cb;
    tref_init(&cb->ref_count, 1);
    return builder;
}

TStringBuilder tstr_builder_new_utf16(size_t capacity)
{
#if TSTR_ENABLE_STRING_SSO
    if (capacity <= TSTR_SMALL_UTF16_MAX_LENGTH) {
        return tstr_builder_new_small_utf16(capacity);
    }
#endif

    size_t bytes = sizeof(TStringInternalControlBlock) + (capacity + 1) * sizeof(uint16_t);
    auto cb = reinterpret_cast<TStringInternalControlBlock *>(malloc(bytes));
    if (!cb) {
        return tstr_builder_new_invalid_utf16();
    }
    uint16_t *buffer = reinterpret_cast<uint16_t *>(cb + 1);
    TStringBuilder builder;
    builder.flags = TSTRING_STORAGE_INTERNAL | TSTRING_ENCODING_UTF16;
    tstr_builder_set_buf_utf16(&builder, buffer);
    tstr_builder_set_cap_utf16(&builder, capacity);
    builder.cb = cb;
    tref_init(&cb->ref_count, 1);
    return builder;
}

bool tstr_builder_reallocate_utf8(TStringBuilder *builder_ptr, size_t capacity, [[maybe_unused]] size_t length)
{
#if TSTR_BUILDER_USE_REALLOC
    if (!tstr_builder_valid(*builder_ptr) || tstr_builder_encoding(*builder_ptr) != TSTRING_ENCODING_UTF8)
        [[unlikely]] {
        return false;
    }

#if TSTR_ENABLE_STRING_SSO
    uint32_t mode = tstr_builder_mode(*builder_ptr);
    if (mode == TSTRING_STORAGE_SMALL) {
        TStringBuilder builder = tstr_builder_new_utf8(capacity);
        if (!tstr_builder_valid(builder)) {
            return false;
        }
        size_t needed = std::min({tstr_builder_cap_utf8(*builder_ptr), length, capacity});
        std::copy_n(tstr_builder_buf_utf8(builder_ptr), needed, tstr_builder_mut_buf_utf8(&builder));
        *builder_ptr = builder;
        return true;
    }
#endif

#if TSTR_ENABLE_STRING_SSO
    if (capacity <= TSTR_SMALL_UTF8_MAX_LENGTH) {
        TStringBuilder builder = tstr_builder_new_small_utf8(capacity);
        if (!tstr_builder_valid(builder)) {
            return false;
        }
        size_t needed = std::min({tstr_builder_cap_utf8(*builder_ptr), length, capacity});
        std::copy_n(tstr_builder_buf_utf8(builder_ptr), needed, tstr_builder_mut_buf_utf8(&builder));
        free(builder_ptr->cb);
        *builder_ptr = builder;
        return true;
    }
#endif

    size_t bytes = sizeof(TStringInternalControlBlock) + (capacity + 1) * sizeof(char);
    auto cb = reinterpret_cast<TStringInternalControlBlock *>(realloc(builder_ptr->cb, bytes));
    if (!cb) {
        return false;
    }
    char *buffer = reinterpret_cast<char *>(cb + 1);
    tstr_builder_set_buf_utf8(builder_ptr, buffer);
    tstr_builder_set_cap_utf8(builder_ptr, capacity);
    builder_ptr->cb = cb;
    return true;
#else
    TStringBuilder builder = tstr_builder_new_utf8(capacity);
    if (!tstr_builder_valid(builder)) {
        return false;
    }
    size_t needed = std::min({tstr_builder_cap_utf8(*builder_ptr), length, capacity});
    std::copy_n(tstr_builder_buf_utf8(builder_ptr), needed, tstr_builder_mut_buf_utf8(&builder));
    tstr_builder_drop(*builder_ptr);
    *builder_ptr = builder;
    return true;
#endif
}

bool tstr_builder_reallocate_utf16(TStringBuilder *builder_ptr, size_t capacity, [[maybe_unused]] size_t length)
{
#if TSTR_BUILDER_USE_REALLOC
    if (!tstr_builder_valid(*builder_ptr) || tstr_builder_encoding(*builder_ptr) != TSTRING_ENCODING_UTF16)
        [[unlikely]] {
        return false;
    }

#if TSTR_ENABLE_STRING_SSO
    uint32_t mode = tstr_builder_mode(*builder_ptr);
    if (mode == TSTRING_STORAGE_SMALL) {
        TStringBuilder builder = tstr_builder_new_utf16(capacity);
        if (!tstr_builder_valid(builder)) {
            return false;
        }
        size_t needed = std::min({tstr_builder_cap_utf16(*builder_ptr), length, capacity});
        std::copy_n(tstr_builder_buf_utf16(builder_ptr), needed, tstr_builder_mut_buf_utf16(&builder));
        *builder_ptr = builder;
        return true;
    }
#endif

#if TSTR_ENABLE_STRING_SSO
    if (capacity <= TSTR_SMALL_UTF16_MAX_LENGTH) {
        TStringBuilder builder = tstr_builder_new_small_utf16(capacity);
        if (!tstr_builder_valid(builder)) {
            return false;
        }
        size_t needed = std::min({tstr_builder_cap_utf16(*builder_ptr), length, capacity});
        std::copy_n(tstr_builder_buf_utf16(builder_ptr), needed, tstr_builder_mut_buf_utf16(&builder));
        free(builder_ptr->cb);
        *builder_ptr = builder;
        return true;
    }
#endif

    size_t bytes = sizeof(TStringInternalControlBlock) + (capacity + 1) * sizeof(uint16_t);
    auto cb = reinterpret_cast<TStringInternalControlBlock *>(realloc(builder_ptr->cb, bytes));
    if (!cb) {
        return false;
    }
    uint16_t *buffer = reinterpret_cast<uint16_t *>(cb + 1);
    tstr_builder_set_buf_utf16(builder_ptr, buffer);
    tstr_builder_set_cap_utf16(builder_ptr, capacity);
    builder_ptr->cb = cb;
    return true;
#else
    TStringBuilder builder = tstr_builder_new_utf16(capacity);
    if (!tstr_builder_valid(builder)) {
        return false;
    }
    size_t needed = std::min({tstr_builder_cap_utf16(*builder_ptr), length, capacity});
    std::copy_n(tstr_builder_buf_utf16(builder_ptr), needed, tstr_builder_mut_buf_utf16(&builder));
    tstr_builder_drop(*builder_ptr);
    *builder_ptr = builder;
    return true;
#endif
}

void tstr_builder_drop(TStringBuilder builder)
{
    uint32_t mode = tstr_builder_mode(builder);
    if (mode == TSTRING_STORAGE_INTERNAL) {
        free(builder.cb);
    }
}

TString tstr_builder_finish_utf8(TStringBuilder builder, size_t length)
{
    if (!tstr_builder_valid(builder) || tstr_builder_encoding(builder) != TSTRING_ENCODING_UTF8 ||
        length > tstr_builder_cap_utf8(builder)) [[unlikely]] {
        tstr_builder_drop(builder);
        return tstr_new_invalid_utf8();
    }

    TString tstr;
#if TSTR_ENABLE_STRING_SSO
    uint32_t mode = tstr_builder_mode(builder);
    if (mode == TSTRING_STORAGE_SMALL) {
        tstr.flags = TSTRING_STORAGE_SMALL | TSTRING_ENCODING_UTF8;
        std::copy_n(tstr_builder_buf_utf8(&builder), length, tstr.small_utf8);
        tstr.small_utf8[length] = '\0';
        tstr_set_len_utf8(&tstr, length);
        return tstr;
    }
#endif

#if TSTR_ENABLE_STRING_SSO
    if (length <= TSTR_SMALL_UTF8_MAX_LENGTH) {
        tstr.flags = TSTRING_STORAGE_SMALL | TSTRING_ENCODING_UTF8;
        std::copy_n(tstr_builder_buf_utf8(&builder), length, tstr.small_utf8);
        tstr.small_utf8[length] = '\0';
        free(builder.cb);
        tstr_set_len_utf8(&tstr, length);
        return tstr;
    }
#endif

    tstr.flags = TSTRING_STORAGE_INTERNAL | TSTRING_ENCODING_UTF8;
    tstr.cb_int = builder.cb;
    tstr_builder_mut_buf_utf8(&builder)[length] = '\0';
    tstr_set_buf_utf8(&tstr, tstr_builder_buf_utf8(&builder));
    tstr_set_len_utf8(&tstr, length);
    return tstr;
}

TString tstr_builder_finish_utf16(TStringBuilder builder, size_t length)
{
    if (!tstr_builder_valid(builder) || tstr_builder_encoding(builder) != TSTRING_ENCODING_UTF16 ||
        length > tstr_builder_cap_utf16(builder)) [[unlikely]] {
        tstr_builder_drop(builder);
        return tstr_new_invalid_utf16();
    }

    TString tstr;
#if TSTR_ENABLE_STRING_SSO
    uint32_t mode = tstr_builder_mode(builder);
    if (mode == TSTRING_STORAGE_SMALL) {
        tstr.flags = TSTRING_STORAGE_SMALL | TSTRING_ENCODING_UTF16;
        std::copy_n(tstr_builder_buf_utf16(&builder), length, tstr.small_utf16);
        tstr.small_utf16[length] = '\0';
        tstr_set_len_utf16(&tstr, length);
        return tstr;
    }
#endif

#if TSTR_ENABLE_STRING_SSO
    if (length <= TSTR_SMALL_UTF16_MAX_LENGTH) {
        tstr.flags = TSTRING_STORAGE_SMALL | TSTRING_ENCODING_UTF16;
        std::copy_n(tstr_builder_buf_utf16(&builder), length, tstr.small_utf16);
        tstr.small_utf16[length] = '\0';
        free(builder.cb);
        tstr_set_len_utf16(&tstr, length);
        return tstr;
    }
#endif

    tstr.flags = TSTRING_STORAGE_INTERNAL | TSTRING_ENCODING_UTF16;
    tstr.cb_int = builder.cb;
    tstr_builder_mut_buf_utf16(&builder)[length] = '\0';
    tstr_set_buf_utf16(&tstr, tstr_builder_buf_utf16(&builder));
    tstr_set_len_utf16(&tstr, length);
    return tstr;
}

#if TSTR_ENABLE_STRING_SSO
TString tstr_new_small_utf8(char const *value TH_NONNULL, size_t len)
{
    TStringBuilder builder = tstr_builder_new_small_utf8(len);
    if (!tstr_builder_valid(builder)) [[unlikely]] {
        return tstr_new_invalid_utf8();
    }
    char *buf = tstr_builder_mut_buf_utf8(&builder);
    char *end = std::copy_n(value, len, buf);
    return tstr_builder_finish_utf8(builder, end - buf);
}

TString tstr_new_small_utf16(uint16_t const *value TH_NONNULL, size_t len)
{
    TStringBuilder builder = tstr_builder_new_small_utf16(len);
    if (!tstr_builder_valid(builder)) [[unlikely]] {
        return tstr_new_invalid_utf16();
    }
    uint16_t *buf = tstr_builder_mut_buf_utf16(&builder);
    uint16_t *end = std::copy_n(value, len, buf);
    return tstr_builder_finish_utf16(builder, end - buf);
}
#endif

TString tstr_new_utf8(char const *value TH_NONNULL, size_t len)
{
#if TSTR_ENABLE_STRING_SSO
    if (len <= TSTR_SMALL_UTF8_MAX_LENGTH) {
        return tstr_new_small_utf8(value, len);
    }
#endif

    TStringBuilder builder = tstr_builder_new_utf8(len);
    if (!tstr_builder_valid(builder)) [[unlikely]] {
        return tstr_new_invalid_utf8();
    }
    char *buf = tstr_builder_mut_buf_utf8(&builder);
    char *end = std::copy_n(value, len, buf);
    return tstr_builder_finish_utf8(builder, end - buf);
}

TString tstr_new_utf16(uint16_t const *value TH_NONNULL, size_t len)
{
#if TSTR_ENABLE_STRING_SSO
    if (len <= TSTR_SMALL_UTF16_MAX_LENGTH) {
        return tstr_new_small_utf16(value, len);
    }
#endif

    TStringBuilder builder = tstr_builder_new_utf16(len);
    if (!tstr_builder_valid(builder)) [[unlikely]] {
        return tstr_new_invalid_utf16();
    }
    uint16_t *buf = tstr_builder_mut_buf_utf16(&builder);
    uint16_t *end = std::copy_n(value, len, buf);
    return tstr_builder_finish_utf16(builder, end - buf);
}

TString tstr_new_borrowed_utf8(char const *buf TH_NONNULL, size_t len)
{
    TString tstr;
    tstr.flags = TSTRING_STORAGE_BORROWED | TSTRING_ENCODING_UTF8;
    tstr_set_buf_utf8(&tstr, buf);
    tstr_set_len_utf8(&tstr, len);
    return tstr;
}

TString tstr_new_borrowed_utf16(uint16_t const *buf TH_NONNULL, size_t len)
{
    TString tstr;
    tstr.flags = TSTRING_STORAGE_BORROWED | TSTRING_ENCODING_UTF16;
    tstr_set_buf_utf16(&tstr, buf);
    tstr_set_len_utf16(&tstr, len);
    return tstr;
}

TString tstr_new_from_external_utf8(char const *buf TH_NONNULL, size_t len, void *context, void (*drop)(void *))
{
#if TSTR_ENABLE_STRING_SSO
    if (len <= TSTR_SMALL_UTF8_MAX_LENGTH) {
        TString result = tstr_new_small_utf8(buf, len);
        if (drop != nullptr) {
            drop(context);
        }
        return result;
    }
#endif

    size_t bytes = sizeof(TStringExternalControlBlock);
    auto cb = reinterpret_cast<TStringExternalControlBlock *>(malloc(bytes));
    if (!cb) {
        if (drop != nullptr) {
            drop(context);
        }
        return tstr_new_invalid_utf8();
    }
    TString tstr;
    tstr.flags = TSTRING_STORAGE_EXTERNAL | TSTRING_ENCODING_UTF8;
    tstr_set_buf_utf8(&tstr, buf);
    tstr_set_len_utf8(&tstr, len);
    tstr.cb_ext = cb;
    tref_init(&cb->ref_count, 1);
    cb->drop = drop;
    cb->context = context;
    return tstr;
}

TString tstr_new_from_external_utf16(uint16_t const *buf TH_NONNULL, size_t len, void *context, void (*drop)(void *))
{
#if TSTR_ENABLE_STRING_SSO
    if (len <= TSTR_SMALL_UTF16_MAX_LENGTH) {
        TString result = tstr_new_small_utf16(buf, len);
        if (drop != nullptr) {
            drop(context);
        }
        return result;
    }
#endif

    size_t bytes = sizeof(TStringExternalControlBlock);
    auto cb = reinterpret_cast<TStringExternalControlBlock *>(malloc(bytes));
    if (!cb) {
        if (drop != nullptr) {
            drop(context);
        }
        return tstr_new_invalid_utf16();
    }
    TString tstr;
    tstr.flags = TSTRING_STORAGE_EXTERNAL | TSTRING_ENCODING_UTF16;
    tstr_set_buf_utf16(&tstr, buf);
    tstr_set_len_utf16(&tstr, len);
    tstr.cb_ext = cb;
    tref_init(&cb->ref_count, 1);
    cb->drop = drop;
    cb->context = context;
    return tstr;
}

TString tstr_new_from_static_utf8(char const *buf TH_NONNULL, size_t len)
{
    TString tstr;
    tstr.flags = TSTRING_STORAGE_STATIC | TSTRING_ENCODING_UTF8;
    tstr_set_buf_utf8(&tstr, buf);
    tstr_set_len_utf8(&tstr, len);
    return tstr;
}

TString tstr_new_from_static_utf16(uint16_t const *buf TH_NONNULL, size_t len)
{
    TString tstr;
    tstr.flags = TSTRING_STORAGE_STATIC | TSTRING_ENCODING_UTF16;
    tstr_set_buf_utf16(&tstr, buf);
    tstr_set_len_utf16(&tstr, len);
    return tstr;
}

TString tstr_dup(TString tstr)
{
    uint32_t mode = tstr_mode(tstr);
    if (mode == TSTRING_STORAGE_BORROWED) {
        uint32_t encoding = tstr_encoding(tstr);
        if (encoding == TSTRING_ENCODING_UTF8) {
            return tstr_new_utf8(tstr_buf_utf8(&tstr), tstr_len_utf8(tstr));
        }
        if (encoding == TSTRING_ENCODING_UTF16) {
            return tstr_new_utf16(tstr_buf_utf16(&tstr), tstr_len_utf16(tstr));
        }
        return tstr_new_invalid(encoding);
    }
    if (mode == TSTRING_STORAGE_INTERNAL) {
        tref_inc(&tstr.cb_int->ref_count);
    }
    if (mode == TSTRING_STORAGE_EXTERNAL) {
        tref_inc(&tstr.cb_ext->ref_count);
    }
    return tstr;
}

void tstr_drop(TString tstr)
{
    uint32_t mode = tstr_mode(tstr);
    if (mode == TSTRING_STORAGE_INTERNAL) {
        TStringInternalControlBlock *cb = tstr.cb_int;
        if (tref_dec(&cb->ref_count)) {
            free(cb);
        }
    }
    if (mode == TSTRING_STORAGE_EXTERNAL) {
        TStringExternalControlBlock *cb = tstr.cb_ext;
        if (tref_dec(&cb->ref_count)) {
            if (cb->drop != nullptr) {
                cb->drop(cb->context);
            }
            free(cb);
        }
    }
}

namespace {
constexpr size_t UTF8_FAST_WORD_SIZE = sizeof(uint64_t) / sizeof(uint8_t);
constexpr size_t UTF8_FAST_BLOCK_SIZE = UTF8_FAST_WORD_SIZE * 2;
constexpr uint64_t UTF8_FAST_ASCII_MASK = 0x8080808080808080;

constexpr size_t UTF16_FAST_WORD_SIZE = sizeof(uint64_t) / sizeof(uint16_t);
constexpr size_t UTF16_FAST_BLOCK_SIZE = UTF16_FAST_WORD_SIZE * 2;
constexpr uint64_t UTF16_FAST_ASCII_MASK = 0xff80ff80ff80ff80;

constexpr uint8_t UTF8_ASCII_PREFIX_MASK = 0b10000000;
constexpr uint8_t UTF8_ASCII_PREFIX = 0b00000000;
constexpr uint8_t UTF8_ASCII_PAYLOAD_MASK = 0b01111111;
constexpr uint8_t UTF8_TWO_BYTE_PREFIX_MASK = 0b11100000;
constexpr uint8_t UTF8_TWO_BYTE_PREFIX = 0b11000000;
constexpr uint8_t UTF8_TWO_BYTE_PAYLOAD_MASK = 0b00011111;
constexpr uint8_t UTF8_THREE_BYTE_PREFIX_MASK = 0b11110000;
constexpr uint8_t UTF8_THREE_BYTE_PREFIX = 0b11100000;
constexpr uint8_t UTF8_THREE_BYTE_PAYLOAD_MASK = 0b00001111;
constexpr uint8_t UTF8_FOUR_BYTE_PREFIX_MASK = 0b11111000;
constexpr uint8_t UTF8_FOUR_BYTE_PREFIX = 0b11110000;
constexpr uint8_t UTF8_FOUR_BYTE_PAYLOAD_MASK = 0b00000111;
constexpr uint8_t UTF8_CONTINUATION_PREFIX_MASK = 0b11000000;
constexpr uint8_t UTF8_CONTINUATION_PREFIX = 0b10000000;
constexpr uint8_t UTF8_CONTINUATION_MASK = 0b00111111;

constexpr uint32_t UTF8_TWO_BYTE_MIN = 0x80;
constexpr uint32_t UTF8_TWO_BYTE_MAX = 0x7ff;
constexpr uint32_t UTF8_THREE_BYTE_MIN = 0x800;
constexpr uint32_t UTF8_THREE_BYTE_MAX = 0xffff;
constexpr uint32_t UTF8_FOUR_BYTE_MIN = 0x10000;
constexpr uint32_t UTF8_FOUR_BYTE_MAX = 0x10ffff;
constexpr uint32_t UTF16_SURROGATE_MIN = 0xd800;
constexpr uint32_t UTF16_SURROGATE_MAX = 0xdfff;

constexpr uint16_t UTF16_NON_ASCII_MASK = 0xff80;
constexpr uint16_t UTF16_THREE_BYTE_MASK = 0xf800;
constexpr uint32_t UTF16_SURROGATE_PREFIX = 0xd800;

constexpr uint32_t UTF16_SURROGATE_PREFIX_MASK = 0xfc00;
constexpr uint32_t UTF16_SURROGATE_PREFIX_HI = 0xd800;
constexpr uint32_t UTF16_SURROGATE_PREFIX_LO = 0xdc00;

constexpr uint32_t UTF16_SURROGATE_SHIFT_HI = 10;
constexpr uint32_t UTF16_SURROGATE_SHIFT_LO = 0;
constexpr uint32_t UTF16_SURROGATE_MASK = 0x3ff;

constexpr uint32_t UTF8_SHIFT_0 = 0;
constexpr uint32_t UTF8_SHIFT_1 = 6;
constexpr uint32_t UTF8_SHIFT_2 = 12;
constexpr uint32_t UTF8_SHIFT_3 = 18;

constexpr uint16_t UNICODE_REPLACEMENT_CHAR = 0xfffd;
constexpr uint8_t UTF8_REPLACEMENT_BYTE_A = 0xef;
constexpr uint8_t UTF8_REPLACEMENT_BYTE_B = 0xbf;
constexpr uint8_t UTF8_REPLACEMENT_BYTE_C = 0xbd;

struct utf16_counter {
    explicit utf16_counter() : count(0)
    {
    }

    void write(uint16_t)
    {
        count++;
    }

    size_t result()
    {
        return count;
    }

private:
    size_t count;
};

struct utf16_writer {
    explicit utf16_writer(uint16_t *output) : output(output)
    {
    }

    void write(uint16_t value)
    {
        *output++ = value;
    }

    uint16_t *result()
    {
        return output;
    }

private:
    uint16_t *output;
};

template<typename Sink, typename... Args>
auto utf8_to_utf16(char const *buf, size_t len, Args &&...args)
{
    uint8_t const *pos = reinterpret_cast<uint8_t const *>(buf);
    uint8_t const *end = reinterpret_cast<uint8_t const *>(buf + len);
    Sink sink(std::forward<Args>(args)...);

    while (pos < end) {
        if (pos + UTF8_FAST_BLOCK_SIZE <= end) {
            uint64_t v = 0;
            for (size_t offset = 0; offset < UTF8_FAST_BLOCK_SIZE; offset += UTF8_FAST_WORD_SIZE) {
                uint64_t t;
                std::copy_n(pos + offset, UTF8_FAST_WORD_SIZE, reinterpret_cast<uint8_t *>(&t));
                v |= t;
            }
            if ((v & UTF8_FAST_ASCII_MASK) == 0) {
                uint8_t const *fin = pos + UTF8_FAST_BLOCK_SIZE;
                while (pos < fin) {
                    sink.write(uint16_t(*pos++));
                }
                continue;
            }
        }

        if ((*pos & UTF8_ASCII_PREFIX_MASK) == UTF8_ASCII_PREFIX) {
            uint32_t codepoint = *pos++ & UTF8_ASCII_PAYLOAD_MASK;
            sink.write(uint16_t(codepoint));
        } else if ((*pos & UTF8_TWO_BYTE_PREFIX_MASK) == UTF8_TWO_BYTE_PREFIX) {
            uint32_t codepoint = (*pos++ & UTF8_TWO_BYTE_PAYLOAD_MASK) << UTF8_SHIFT_1;
            if (pos >= end || (*pos & UTF8_CONTINUATION_PREFIX_MASK) != UTF8_CONTINUATION_PREFIX) {
                sink.write(UNICODE_REPLACEMENT_CHAR);
                continue;
            }
            codepoint |= (*pos++ & UTF8_CONTINUATION_MASK) << UTF8_SHIFT_0;
            if (codepoint < UTF8_TWO_BYTE_MIN || codepoint > UTF8_TWO_BYTE_MAX) {
                sink.write(UNICODE_REPLACEMENT_CHAR);
                continue;
            }
            sink.write(uint16_t(codepoint));
        } else if ((*pos & UTF8_THREE_BYTE_PREFIX_MASK) == UTF8_THREE_BYTE_PREFIX) {
            uint32_t codepoint = (*pos++ & UTF8_THREE_BYTE_PAYLOAD_MASK) << UTF8_SHIFT_2;
            if (pos >= end || (*pos & UTF8_CONTINUATION_PREFIX_MASK) != UTF8_CONTINUATION_PREFIX) {
                sink.write(UNICODE_REPLACEMENT_CHAR);
                continue;
            }
            codepoint |= (*pos++ & UTF8_CONTINUATION_MASK) << UTF8_SHIFT_1;
            if (pos >= end || (*pos & UTF8_CONTINUATION_PREFIX_MASK) != UTF8_CONTINUATION_PREFIX) {
                sink.write(UNICODE_REPLACEMENT_CHAR);
                continue;
            }
            codepoint |= (*pos++ & UTF8_CONTINUATION_MASK) << UTF8_SHIFT_0;
            if (codepoint < UTF8_THREE_BYTE_MIN || codepoint > UTF8_THREE_BYTE_MAX ||
                (codepoint >= UTF16_SURROGATE_MIN && codepoint <= UTF16_SURROGATE_MAX)) {
                sink.write(UNICODE_REPLACEMENT_CHAR);
                continue;
            }
            sink.write(uint16_t(codepoint));
        } else if ((*pos & UTF8_FOUR_BYTE_PREFIX_MASK) == UTF8_FOUR_BYTE_PREFIX) {
            uint32_t codepoint = (*pos++ & UTF8_FOUR_BYTE_PAYLOAD_MASK) << UTF8_SHIFT_3;
            if (pos >= end || (*pos & UTF8_CONTINUATION_PREFIX_MASK) != UTF8_CONTINUATION_PREFIX) {
                sink.write(UNICODE_REPLACEMENT_CHAR);
                continue;
            }
            codepoint |= (*pos++ & UTF8_CONTINUATION_MASK) << UTF8_SHIFT_2;
            if (pos >= end || (*pos & UTF8_CONTINUATION_PREFIX_MASK) != UTF8_CONTINUATION_PREFIX) {
                sink.write(UNICODE_REPLACEMENT_CHAR);
                continue;
            }
            codepoint |= (*pos++ & UTF8_CONTINUATION_MASK) << UTF8_SHIFT_1;
            if (pos >= end || (*pos & UTF8_CONTINUATION_PREFIX_MASK) != UTF8_CONTINUATION_PREFIX) {
                sink.write(UNICODE_REPLACEMENT_CHAR);
                continue;
            }
            codepoint |= (*pos++ & UTF8_CONTINUATION_MASK) << UTF8_SHIFT_0;
            if (codepoint < UTF8_FOUR_BYTE_MIN || codepoint > UTF8_FOUR_BYTE_MAX) {
                sink.write(UNICODE_REPLACEMENT_CHAR);
                continue;
            }
            uint32_t surrogate = codepoint - UTF8_FOUR_BYTE_MIN;
            uint32_t surrogate_hi = (surrogate >> UTF16_SURROGATE_SHIFT_HI) & UTF16_SURROGATE_MASK;
            uint32_t surrogate_lo = (surrogate >> UTF16_SURROGATE_SHIFT_LO) & UTF16_SURROGATE_MASK;
            sink.write(uint16_t(UTF16_SURROGATE_PREFIX_HI | surrogate_hi));
            sink.write(uint16_t(UTF16_SURROGATE_PREFIX_LO | surrogate_lo));
        } else {
            pos++;
            sink.write(UNICODE_REPLACEMENT_CHAR);
        }
    }
    return sink.result();
}

inline size_t count_utf8_to_utf16(char const *buf, size_t len)
{
    return utf8_to_utf16<utf16_counter>(buf, len);
}

inline uint16_t *write_utf8_to_utf16(char const *buf, size_t len, uint16_t *output)
{
    return utf8_to_utf16<utf16_writer>(buf, len, output);
}

struct utf8_counter {
    explicit utf8_counter() : count(0)
    {
    }

    void write(char)
    {
        count++;
    }

    size_t result()
    {
        return count;
    }

private:
    size_t count;
};

struct utf8_writer {
    explicit utf8_writer(char *output) : output(output)
    {
    }

    void write(char value)
    {
        *output++ = value;
    }

    char *result()
    {
        return output;
    }

private:
    char *output;
};

template<typename Sink, typename... Args>
auto utf16_to_utf8(uint16_t const *buf, size_t len, Args &&...args)
{
    uint16_t const *pos = buf;
    uint16_t const *end = buf + len;
    Sink sink(std::forward<Args>(args)...);

    while (pos < end) {
        if (pos + UTF16_FAST_BLOCK_SIZE <= end) {
            uint64_t v = 0;
            for (size_t i = 0; i < UTF16_FAST_BLOCK_SIZE; i += UTF16_FAST_WORD_SIZE) {
                uint64_t t;
                std::copy_n(pos + i, UTF16_FAST_WORD_SIZE, reinterpret_cast<uint16_t *>(&t));
                v |= t;
            }
            if ((v & UTF16_FAST_ASCII_MASK) == 0) {
                uint16_t const *fin = pos + UTF16_FAST_BLOCK_SIZE;
                while (pos < fin) {
                    sink.write(char(*pos++));
                }
                continue;
            }
        }

        if ((*pos & UTF16_NON_ASCII_MASK) == 0) {
            uint32_t codepoint = *pos++;
            sink.write(char(codepoint));
        } else if ((*pos & UTF16_THREE_BYTE_MASK) == 0) {
            uint32_t codepoint = *pos++;
            sink.write(char(((codepoint >> UTF8_SHIFT_1) & UTF8_TWO_BYTE_PAYLOAD_MASK) | UTF8_TWO_BYTE_PREFIX));
            sink.write(char(((codepoint >> UTF8_SHIFT_0) & UTF8_CONTINUATION_MASK) | UTF8_CONTINUATION_PREFIX));
        } else if ((*pos & UTF16_THREE_BYTE_MASK) != UTF16_SURROGATE_PREFIX) {
            uint32_t codepoint = *pos++;
            sink.write(char(((codepoint >> UTF8_SHIFT_2) & UTF8_THREE_BYTE_PAYLOAD_MASK) | UTF8_THREE_BYTE_PREFIX));
            sink.write(char(((codepoint >> UTF8_SHIFT_1) & UTF8_CONTINUATION_MASK) | UTF8_CONTINUATION_PREFIX));
            sink.write(char(((codepoint >> UTF8_SHIFT_0) & UTF8_CONTINUATION_MASK) | UTF8_CONTINUATION_PREFIX));
        } else if (pos + 1 < end && (*(pos + 0) & UTF16_SURROGATE_PREFIX_MASK) == UTF16_SURROGATE_PREFIX_HI &&
                   (*(pos + 1) & UTF16_SURROGATE_PREFIX_MASK) == UTF16_SURROGATE_PREFIX_LO) {
            uint32_t surrogate_hi = *pos++ & UTF16_SURROGATE_MASK;
            uint32_t surrogate_lo = *pos++ & UTF16_SURROGATE_MASK;
            uint32_t surrogate =
                (surrogate_hi << UTF16_SURROGATE_SHIFT_HI) | (surrogate_lo << UTF16_SURROGATE_SHIFT_LO);
            uint32_t codepoint = surrogate + UTF8_FOUR_BYTE_MIN;
            sink.write(char(((codepoint >> UTF8_SHIFT_3) & UTF8_FOUR_BYTE_PAYLOAD_MASK) | UTF8_FOUR_BYTE_PREFIX));
            sink.write(char(((codepoint >> UTF8_SHIFT_2) & UTF8_CONTINUATION_MASK) | UTF8_CONTINUATION_PREFIX));
            sink.write(char(((codepoint >> UTF8_SHIFT_1) & UTF8_CONTINUATION_MASK) | UTF8_CONTINUATION_PREFIX));
            sink.write(char(((codepoint >> UTF8_SHIFT_0) & UTF8_CONTINUATION_MASK) | UTF8_CONTINUATION_PREFIX));
        } else {
            pos++;
            sink.write(char(UTF8_REPLACEMENT_BYTE_A));
            sink.write(char(UTF8_REPLACEMENT_BYTE_B));
            sink.write(char(UTF8_REPLACEMENT_BYTE_C));
        }
    }
    return sink.result();
}

inline size_t count_utf16_to_utf8(uint16_t const *buf, size_t len)
{
    return utf16_to_utf8<utf8_counter>(buf, len);
}

inline char *write_utf16_to_utf8(uint16_t const *buf, size_t len, char *output)
{
    return utf16_to_utf8<utf8_writer>(buf, len, output);
}
}  // namespace

TString tstr_dup_as_utf16(TString tstr)
{
    uint32_t encoding = tstr_encoding(tstr);
    if (encoding == TSTRING_ENCODING_UTF16) {
        return tstr_dup(tstr);
    }
    char const *src = tstr_buf_utf8(&tstr);
    size_t len = tstr_len_utf8(tstr);
    if (encoding == TSTRING_ENCODING_UTF8) {
        size_t needed = count_utf8_to_utf16(src, len);
        TStringBuilder builder = tstr_builder_new_utf16(needed);
        if (!tstr_builder_valid(builder)) [[unlikely]] {
            return tstr_new_invalid_utf16();
        }
        uint16_t *dst = tstr_builder_mut_buf_utf16(&builder);
        uint16_t *end = write_utf8_to_utf16(src, len, dst);
        return tstr_builder_finish_utf16(builder, end - dst);
    }
    return tstr_new_invalid_utf16();
}

TString tstr_dup_as_utf8(TString tstr)
{
    uint32_t encoding = tstr_encoding(tstr);
    if (encoding == TSTRING_ENCODING_UTF8) {
        return tstr_dup(tstr);
    }
    uint16_t const *src = tstr_buf_utf16(&tstr);
    size_t len = tstr_len_utf16(tstr);
    if (encoding == TSTRING_ENCODING_UTF16) {
        size_t needed = count_utf16_to_utf8(src, len);
        TStringBuilder builder = tstr_builder_new_utf8(needed);
        if (!tstr_builder_valid(builder)) [[unlikely]] {
            return tstr_new_invalid_utf8();
        }
        char *dst = tstr_builder_mut_buf_utf8(&builder);
        char *end = write_utf16_to_utf8(src, len, dst);
        return tstr_builder_finish_utf8(builder, end - dst);
    }
    return tstr_new_invalid_utf8();
}

TString tstr_concat_as_utf8(size_t count, TString const *tstr_list)
{
    size_t len = 0;
    for (size_t i = 0; i < count; ++i) {
        TString tstr = tstr_list[i];
        uint32_t encoding = tstr_encoding(tstr);
        if (encoding == TSTRING_ENCODING_UTF8) {
            len += tstr_len_utf8(tstr);
        } else if (encoding == TSTRING_ENCODING_UTF16) {
            len += count_utf16_to_utf8(tstr_buf_utf16(&tstr), tstr_len_utf16(tstr));
        } else {
            return tstr_new_invalid_utf8();
        }
    }
    TStringBuilder builder = tstr_builder_new_utf8(len);
    if (!tstr_builder_valid(builder)) [[unlikely]] {
        return tstr_new_invalid_utf8();
    }
    char *buf = tstr_builder_mut_buf_utf8(&builder);
    char *end = buf;
    for (size_t i = 0; i < count; ++i) {
        TString tstr = tstr_list[i];
        uint32_t encoding = tstr_encoding(tstr);
        if (encoding == TSTRING_ENCODING_UTF8) {
            end = std::copy_n(tstr_buf_utf8(&tstr), tstr_len_utf8(tstr), end);
        } else if (encoding == TSTRING_ENCODING_UTF16) {
            end = write_utf16_to_utf8(tstr_buf_utf16(&tstr), tstr_len_utf16(tstr), end);
        }
    }
    return tstr_builder_finish_utf8(builder, end - buf);
}

TString tstr_concat_as_utf16(size_t count, TString const *tstr_list)
{
    size_t len = 0;
    for (size_t i = 0; i < count; ++i) {
        TString tstr = tstr_list[i];
        uint32_t encoding = tstr_encoding(tstr);
        if (encoding == TSTRING_ENCODING_UTF16) {
            len += tstr_len_utf16(tstr);
        } else if (encoding == TSTRING_ENCODING_UTF8) {
            len += count_utf8_to_utf16(tstr_buf_utf8(&tstr), tstr_len_utf8(tstr));
        } else {
            return tstr_new_invalid_utf16();
        }
    }
    TStringBuilder builder = tstr_builder_new_utf16(len);
    if (!tstr_builder_valid(builder)) [[unlikely]] {
        return tstr_new_invalid_utf16();
    }
    uint16_t *buf = tstr_builder_mut_buf_utf16(&builder);
    uint16_t *end = buf;
    for (size_t i = 0; i < count; ++i) {
        TString tstr = tstr_list[i];
        uint32_t encoding = tstr_encoding(tstr);
        if (encoding == TSTRING_ENCODING_UTF16) {
            end = std::copy_n(tstr_buf_utf16(&tstr), tstr_len_utf16(tstr), end);
        } else if (encoding == TSTRING_ENCODING_UTF8) {
            end = write_utf8_to_utf16(tstr_buf_utf8(&tstr), tstr_len_utf8(tstr), end);
        }
    }
    return tstr_builder_finish_utf16(builder, end - buf);
}

TString tstr_substr_utf8(TString tstr, size_t pos, size_t len)
{
    if (tstr_encoding(tstr) != TSTRING_ENCODING_UTF8) {
        return tstr_new_invalid_utf8();
    }

    size_t const orig_len = tstr_len_utf8(tstr);
    if (pos > orig_len) {
        pos = orig_len;
    }
    size_t const remaining = orig_len - pos;
    if (len > remaining) {
        len = remaining;
    }

#if TSTR_ENABLE_STRING_SSO
    uint32_t mode = tstr_mode(tstr);
    // An SSO buffer is embedded in the by-value input, so it must be copied.
    if (mode == TSTRING_STORAGE_SMALL) {
        return tstr_new_small_utf8(tstr_buf_utf8(&tstr) + pos, len);
    }
#endif

#if TSTR_ENABLE_RETAINABLE_SUBSTR
#if TSTR_ENABLE_STRING_SSO
    // Sharing a short ref-counted slice would bypass SSO, so we do it explicitly here.
    if ((len <= TSTR_SMALL_UTF8_MAX_LENGTH && (mode == TSTRING_STORAGE_INTERNAL || mode == TSTRING_STORAGE_EXTERNAL))) {
        return tstr_new_small_utf8(tstr_buf_utf8(&tstr) + pos, len);
    }
#endif

    // Preserve storage metadata so a later tstr_dup can share the storage.
    // No ownership reference is acquired for this view.
    tstr_set_buf_utf8(&tstr, tstr_buf_utf8(&tstr) + pos);
    tstr_set_len_utf8(&tstr, len);
    return tstr;
#else
    // We don't need to do SSO for borrowed strings since tstr_dup will do it for us.
    return tstr_new_borrowed_utf8(tstr_buf_utf8(&tstr) + pos, len);
#endif
}

TString tstr_substr_utf16(TString tstr, size_t pos, size_t len)
{
    if (tstr_encoding(tstr) != TSTRING_ENCODING_UTF16) {
        return tstr_new_invalid_utf16();
    }

    size_t const orig_len = tstr_len_utf16(tstr);
    if (pos > orig_len) {
        pos = orig_len;
    }
    size_t const remaining = orig_len - pos;
    if (len > remaining) {
        len = remaining;
    }

#if TSTR_ENABLE_STRING_SSO
    uint32_t mode = tstr_mode(tstr);
    // An SSO buffer is embedded in the by-value input, so it must be copied.
    if (mode == TSTRING_STORAGE_SMALL) {
        return tstr_new_small_utf16(tstr_buf_utf16(&tstr) + pos, len);
    }
#endif

#if TSTR_ENABLE_RETAINABLE_SUBSTR
#if TSTR_ENABLE_STRING_SSO
    // Sharing a short ref-counted slice would bypass SSO, so we do it explicitly here.
    if ((len <= TSTR_SMALL_UTF16_MAX_LENGTH &&
         (mode == TSTRING_STORAGE_INTERNAL || mode == TSTRING_STORAGE_EXTERNAL))) {
        return tstr_new_small_utf16(tstr_buf_utf16(&tstr) + pos, len);
    }
#endif

    // Preserve storage metadata so a later tstr_dup can share the storage.
    // No ownership reference is acquired for this view.
    tstr_set_buf_utf16(&tstr, tstr_buf_utf16(&tstr) + pos);
    tstr_set_len_utf16(&tstr, len);
    return tstr;
#else
    // We don't need to do SSO for borrowed strings since tstr_dup will do it for us.
    return tstr_new_borrowed_utf16(tstr_buf_utf16(&tstr) + pos, len);
#endif
}
