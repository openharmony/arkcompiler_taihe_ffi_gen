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

TH_INLINE void tstr_set_data(TString *tstr_ptr, void const *data)
{
    tstr_ptr->data = data;
}

TH_INLINE void tstr_set_buf_utf8(TString *tstr_ptr, char const *buf)
{
    tstr_set_data(tstr_ptr, buf);
}

TH_INLINE void tstr_set_buf_utf16(TString *tstr_ptr, uint16_t const *buf)
{
    tstr_set_data(tstr_ptr, buf);
}

TH_INLINE void tstr_set_byte_length(TString *tstr_ptr, size_t byte_length)
{
    tstr_ptr->byte_length = byte_length;
}

TH_INLINE void tstr_set_len_utf8(TString *tstr_ptr, size_t len)
{
    tstr_set_byte_length(tstr_ptr, len * sizeof(char));
}

TH_INLINE void tstr_set_len_utf16(TString *tstr_ptr, size_t len)
{
    tstr_set_byte_length(tstr_ptr, len * sizeof(uint16_t));
}

TH_INLINE uint32_t tstr_mode(TString tstr)
{
    return tstr.flags & TSTRING_STORAGE_MASK;
}

TH_INLINE uint32_t tstr_is_valid(TString tstr)
{
    return tstr_mode(tstr) != TSTRING_STORAGE_INVALID;
}

TString tstr_new_invalid()
{
    TString tstr;
    tstr.flags = TSTRING_STORAGE_INVALID | TSTRING_ENCODING_UNKNOWN;
    tstr_set_byte_length(&tstr, 0);
    tstr_set_data(&tstr, nullptr);
    return tstr;
}

TString tstr_new_static(uint32_t encoding, void const *buf TH_NONNULL, size_t byte_length)
{
    TString tstr;
    tstr.flags = TSTRING_STORAGE_STATIC | (encoding & TSTRING_ENCODING_MASK);
    tstr_set_data(&tstr, buf);
    tstr_set_byte_length(&tstr, byte_length);
    return tstr;
}

TString tstr_new_static_utf8(char const *buf TH_NONNULL, size_t len)
{
    return tstr_new_static(TSTRING_ENCODING_UTF8, buf, len * sizeof(char));
}

TString tstr_new_static_utf16(uint16_t const *buf TH_NONNULL, size_t len)
{
    return tstr_new_static(TSTRING_ENCODING_UTF16, buf, len * sizeof(uint16_t));
}

TString tstr_new_internal_impl(uint32_t encoding, void const *data TH_NONNULL, size_t byte_length,
                               struct TStringInternalControlBlock *cb TH_NONNULL)
{
    TString tstr;
    tstr.flags = TSTRING_STORAGE_INTERNAL | (encoding & TSTRING_ENCODING_MASK);
    tstr_set_data(&tstr, data);
    tstr_set_byte_length(&tstr, byte_length);
    tstr.internal_cb = cb;
    return tstr;
}

TString tstr_new_acquired_impl(uint32_t encoding, void const *data TH_NONNULL, size_t byte_length,
                               struct TStringAcquiredControlBlock *cb TH_NONNULL)
{
    TString tstr;
    tstr.flags = TSTRING_STORAGE_ACQUIRED | (encoding & TSTRING_ENCODING_MASK);
    tstr_set_data(&tstr, data);
    tstr_set_byte_length(&tstr, byte_length);
    tstr.acquired_cb = cb;
    return tstr;
}

void tstr_global_context_release(struct TStringGlobalRefContext ctx)
{
    ctx.release(ctx.ref);
}

struct TStringAcquiredControlBlock *tstr_acquired_control_block_new(struct TStringGlobalRefContext ctx)
{
    size_t required = sizeof(struct TStringAcquiredControlBlock);
    auto cb = reinterpret_cast<struct TStringAcquiredControlBlock *>(malloc(required));
    if (!cb) {
        tstr_global_context_release(ctx);
        return nullptr;
    }
    tref_init(&cb->ref_count, 1);
    cb->global_ctx = ctx;
    return cb;
}

TString tstr_new_acquired(uint32_t encoding, void const *data TH_NONNULL, size_t byte_length,
                          struct TStringGlobalRefContext ctx)
{
    auto cb = tstr_acquired_control_block_new(ctx);
    if (!cb) {
        return tstr_new_invalid();
    }
    return tstr_new_acquired_impl(encoding, data, byte_length, cb);
}

TString tstr_new_acquired_utf8(char const *buf TH_NONNULL, size_t len, struct TStringGlobalRefContext ctx)
{
    return tstr_new_acquired(TSTRING_ENCODING_UTF8, buf, len * sizeof(char), ctx);
}

TString tstr_new_acquired_utf16(uint16_t const *buf TH_NONNULL, size_t len, struct TStringGlobalRefContext ctx)
{
    return tstr_new_acquired(TSTRING_ENCODING_UTF16, buf, len * sizeof(uint16_t), ctx);
}

void tstr_acquire_cache_init(struct TStringAcquireCache *cache TH_NONNULL, struct TStringLocalRefContext ctx)
{
    cache->acquired_cb = nullptr;
    cache->local_ctx = ctx;
}

TString tstr_new_acquirable_borrowed(uint32_t encoding, void const *data TH_NONNULL, size_t byte_length,
                                     struct TStringAcquireCache *cache TH_NONNULL, struct TStringLocalRefContext ctx)
{
    TString tstr;
    tstr.flags = TSTRING_STORAGE_ACQUIRABLE_BORROWED | (encoding & TSTRING_ENCODING_MASK);
    tstr_set_data(&tstr, data);
    tstr_set_byte_length(&tstr, byte_length);
    tstr.acquire_cache = cache;
    tstr_acquire_cache_init(cache, ctx);
    return tstr;
}

TString tstr_new_acquirable_borrowed_utf8(char const *buf TH_NONNULL, size_t len,
                                          struct TStringAcquireCache *cache TH_NONNULL,
                                          struct TStringLocalRefContext ctx)
{
    return tstr_new_acquirable_borrowed(TSTRING_ENCODING_UTF8, buf, len * sizeof(char), cache, ctx);
}

TString tstr_new_acquirable_borrowed_utf16(uint16_t const *buf TH_NONNULL, size_t len,
                                           struct TStringAcquireCache *cache TH_NONNULL,
                                           struct TStringLocalRefContext ctx)
{
    return tstr_new_acquirable_borrowed(TSTRING_ENCODING_UTF16, buf, len * sizeof(uint16_t), cache, ctx);
}

void tstr_copy_cache_init(struct TStringCopyCache *cache, TString original)
{
    if (cache == nullptr) {
        return;
    }
    cache->copied = tstr_new_invalid();
    cache->original = original;
}

TString tstr_new_copyable_borrowed(uint32_t encoding, void const *data TH_NONNULL, size_t byte_length,
                                   struct TStringCopyCache *cache)
{
    TString tstr;
    tstr.flags = TSTRING_STORAGE_COPIABLE_BORROWED | (encoding & TSTRING_ENCODING_MASK);
    tstr_set_data(&tstr, data);
    tstr_set_byte_length(&tstr, byte_length);
    tstr.copy_cache = cache;
    tstr_copy_cache_init(cache, tstr);
    return tstr;
}

TString tstr_new_copyable_borrowed_utf8(char const *buf TH_NONNULL, size_t len, struct TStringCopyCache *cache)
{
    return tstr_new_copyable_borrowed(TSTRING_ENCODING_UTF8, buf, len * sizeof(char), cache);
}

TString tstr_new_copyable_borrowed_utf16(uint16_t const *buf TH_NONNULL, size_t len, struct TStringCopyCache *cache)
{
    return tstr_new_copyable_borrowed(TSTRING_ENCODING_UTF16, buf, len * sizeof(uint16_t), cache);
}

TString tstr_substr_impl(uint32_t encoding, TString tstr, size_t byte_offset, size_t byte_length)
{
    tstr.flags = (tstr.flags & ~TSTRING_ENCODING_MASK) | (encoding & TSTRING_ENCODING_MASK);
    tstr_set_data(&tstr, reinterpret_cast<std::byte const *>(tstr_data(tstr)) + byte_offset);
    tstr_set_byte_length(&tstr, byte_length);
    return tstr;
}

TString tstr_substr(uint32_t encoding, TString tstr, size_t byte_offset, size_t byte_length,
                    struct TStringCopyCache *cache)
{
    if (!tstr_is_valid(tstr)) {
        tstr_copy_cache_init(cache, tstr_new_invalid());
        return tstr_new_invalid();
    }
    size_t byte_original = tstr_byte_length(tstr);
    if (byte_offset > byte_original) {
        tstr_copy_cache_init(cache, tstr_new_invalid());
        return tstr_new_invalid();
    }
    size_t byte_remaining = byte_original - byte_offset;
    if (byte_length > byte_remaining) {
        byte_length = byte_remaining;
    }
#if TSTR_ENABLE_RETAINABLE_SUBSTR
    uint32_t mode = tstr_mode(tstr);
    if (mode != TSTRING_STORAGE_COPIABLE_BORROWED || tstr.copy_cache != nullptr) {
        tstr_copy_cache_init(cache, tstr_new_invalid());
        return tstr_substr_impl(encoding, tstr, byte_offset, byte_length);
    }
#endif
    return tstr_new_copyable_borrowed(encoding, reinterpret_cast<std::byte const *>(tstr_data(tstr)) + byte_offset,
                                      byte_length, cache);
}

TString tstr_substr_utf8(TString tstr, size_t pos, size_t len, struct TStringCopyCache *cache)
{
    return tstr_substr(TSTRING_ENCODING_UTF8, tstr, pos * sizeof(char), len * sizeof(char), cache);
}

TString tstr_substr_utf16(TString tstr, size_t pos, size_t len, struct TStringCopyCache *cache)
{
    return tstr_substr(TSTRING_ENCODING_UTF16, tstr, pos * sizeof(uint16_t), len * sizeof(uint16_t), cache);
}

struct TStringGlobalRefContext tstr_local_context_acquire(struct TStringLocalRefContext ctx)
{
    return ctx.acquire(ctx.ref);
}

TString tstr_acquire_cache_get_relative(uint32_t encoding, void const *data TH_NONNULL, size_t byte_length,
                                        struct TStringAcquireCache *cache TH_NONNULL)
{
    if (cache->acquired_cb == nullptr) {
        struct TStringGlobalRefContext ctx = tstr_local_context_acquire(cache->local_ctx);
        cache->acquired_cb = tstr_acquired_control_block_new(ctx);
        if (cache->acquired_cb == nullptr) {
            return tstr_new_invalid();
        }
    }
    return tstr_new_acquired_impl(encoding, data, byte_length, cache->acquired_cb);
}

TString tstr_copy(TString tstr)
{
    uint32_t encoding = tstr_encoding(tstr);
    if (encoding == TSTRING_ENCODING_UTF8) {
        return tstr_new_copied_utf8(tstr_buf_utf8(tstr), tstr_len_utf8(tstr));
    }
    if (encoding == TSTRING_ENCODING_UTF16) {
        return tstr_new_copied_utf16(tstr_buf_utf16(tstr), tstr_len_utf16(tstr));
    }
    return tstr_new_invalid();
}

TString tstr_copy_cache_get_relative(uint32_t encoding, void const *data TH_NONNULL, size_t byte_length,
                                     struct TStringCopyCache *cache TH_NONNULL)
{
    if (!tstr_is_valid(cache->copied)) {
        cache->copied = tstr_copy(cache->original);
        if (!tstr_is_valid(cache->copied)) {
            return tstr_new_invalid();
        }
    }
    return tstr_substr_impl(
        encoding, cache->copied,
        reinterpret_cast<std::byte const *>(data) - reinterpret_cast<std::byte const *>(tstr_data(cache->original)),
        byte_length);
}

struct TStringInternalControlBlock *tstr_internal_control_block_dup(struct TStringInternalControlBlock *cb TH_NONNULL)
{
    tref_inc(&cb->ref_count);
    return cb;
}

struct TStringAcquiredControlBlock *tstr_acquired_control_block_dup(struct TStringAcquiredControlBlock *cb TH_NONNULL)
{
    tref_inc(&cb->ref_count);
    return cb;
}

TString tstr_dup(TString tstr)
{
    uint32_t mode = tstr_mode(tstr);
    if (mode == TSTRING_STORAGE_STATIC) {
        return tstr;
    }
    if (mode == TSTRING_STORAGE_INTERNAL) {
        return tstr_new_internal_impl(tstr_encoding(tstr), tstr_data(tstr), tstr_byte_length(tstr),
                                      tstr_internal_control_block_dup(tstr.internal_cb));
    }
    if (mode == TSTRING_STORAGE_ACQUIRED) {
        return tstr_new_acquired_impl(tstr_encoding(tstr), tstr_data(tstr), tstr_byte_length(tstr),
                                      tstr_acquired_control_block_dup(tstr.acquired_cb));
    }
    if (mode == TSTRING_STORAGE_ACQUIRABLE_BORROWED) {
        return tstr_dup(tstr_acquire_cache_get_relative(tstr_encoding(tstr), tstr_data(tstr), tstr_byte_length(tstr),
                                                        tstr.acquire_cache));
    }
    if (mode == TSTRING_STORAGE_COPIABLE_BORROWED) {
        if (tstr.copy_cache == nullptr) {
            return tstr_copy(tstr);
        }
        return tstr_dup(tstr_copy_cache_get_relative(tstr_encoding(tstr), tstr_data(tstr), tstr_byte_length(tstr),
                                                     tstr.copy_cache));
    }
    return tstr_new_invalid();
}

void tstr_internal_control_block_drop(struct TStringInternalControlBlock *cb TH_NONNULL)
{
    if (tref_dec(&cb->ref_count)) {
        free(cb);
    }
}

void tstr_acquired_control_block_drop(struct TStringAcquiredControlBlock *cb TH_NONNULL)
{
    if (tref_dec(&cb->ref_count)) {
        tstr_global_context_release(cb->global_ctx);
        free(cb);
    }
}

void tstr_drop(TString tstr)
{
    uint32_t mode = tstr_mode(tstr);
    if (mode == TSTRING_STORAGE_INTERNAL) {
        tstr_internal_control_block_drop(tstr.internal_cb);
    }
    if (mode == TSTRING_STORAGE_ACQUIRED) {
        tstr_acquired_control_block_drop(tstr.acquired_cb);
    }
}

void tstr_copy_cache_drop(struct TStringCopyCache const *cache TH_NONNULL)
{
    if (tstr_is_valid(cache->copied)) {
        tstr_drop(cache->copied);
    }
}

void tstr_acquire_cache_drop(struct TStringAcquireCache const *cache TH_NONNULL)
{
    if (cache->acquired_cb != nullptr) {
        tstr_acquired_control_block_drop(cache->acquired_cb);
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
            for (size_t i = 0; i < UTF8_FAST_BLOCK_SIZE; i += UTF8_FAST_WORD_SIZE) {
                uint64_t t;
                std::copy_n(pos + i, UTF8_FAST_WORD_SIZE, reinterpret_cast<uint8_t *>(&t));
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

TH_INLINE void tstr_builder_set_buffer(TStringBuilder *builder_ptr, void *data)
{
    builder_ptr->buffer = data;
}

TH_INLINE void tstr_builder_set_buf_utf8(TStringBuilder *builder_ptr, char *buf)
{
    tstr_builder_set_buffer(builder_ptr, buf);
}

TH_INLINE void tstr_builder_set_buf_utf16(TStringBuilder *builder_ptr, uint16_t *buf)
{
    tstr_builder_set_buffer(builder_ptr, buf);
}

TH_INLINE void tstr_builder_set_byte_capacity(TStringBuilder *builder_ptr, size_t byte_capacity)
{
    builder_ptr->byte_capacity = byte_capacity;
}

TH_INLINE void tstr_builder_set_cap_utf8(TStringBuilder *builder_ptr, size_t cap)
{
    tstr_builder_set_byte_capacity(builder_ptr, cap * sizeof(char));
}

TH_INLINE void tstr_builder_set_cap_utf16(TStringBuilder *builder_ptr, size_t cap)
{
    tstr_builder_set_byte_capacity(builder_ptr, cap * sizeof(uint16_t));
}

TH_INLINE uint32_t tstr_builder_mode(TStringBuilder builder)
{
    return builder.flags & TSTRING_STORAGE_MASK;
}

TH_INLINE uint32_t tstr_builder_is_valid(TStringBuilder builder)
{
    return tstr_builder_mode(builder) != TSTRING_STORAGE_INVALID;
}

TStringBuilder tstr_builder_new_invalid()
{
    TStringBuilder builder;
    builder.flags = TSTRING_STORAGE_INVALID | TSTRING_ENCODING_UNKNOWN;
    tstr_builder_set_byte_capacity(&builder, 0);
    tstr_builder_set_buffer(&builder, nullptr);
    return builder;
}

TStringBuilder tstr_builder_new_impl(uint32_t encoding, void *data, size_t byte_capacity,
                                     struct TStringInternalControlBlock *cb TH_NONNULL)
{
    TStringBuilder builder;
    builder.flags = TSTRING_STORAGE_INTERNAL | (encoding & TSTRING_ENCODING_MASK);
    tstr_builder_set_buffer(&builder, data);
    tstr_builder_set_byte_capacity(&builder, byte_capacity);
    builder.cb = cb;
    return builder;
}

struct TStringInternalControlBlock *tstr_internal_control_block_new(size_t bytes)
{
    size_t required = sizeof(struct TStringInternalControlBlock) + bytes;
    auto cb = reinterpret_cast<struct TStringInternalControlBlock *>(malloc(required));
    if (!cb) {
        return nullptr;
    }
    tref_init(&cb->ref_count, 1);
    return cb;
}

TStringBuilder tstr_builder_new_utf8(size_t cap)
{
    auto cb = tstr_internal_control_block_new((cap + 1) * sizeof(char));
    if (!cb) {
        return tstr_builder_new_invalid();
    }
    char *buf = reinterpret_cast<char *>(cb + 1);
    return tstr_builder_new_impl(TSTRING_ENCODING_UTF8, buf, cap * sizeof(char), cb);
}

TStringBuilder tstr_builder_new_utf16(size_t cap)
{
    auto cb = tstr_internal_control_block_new((cap + 1) * sizeof(uint16_t));
    if (!cb) {
        return tstr_builder_new_invalid();
    }
    uint16_t *buf = reinterpret_cast<uint16_t *>(cb + 1);
    return tstr_builder_new_impl(TSTRING_ENCODING_UTF16, buf, cap * sizeof(uint16_t), cb);
}

#if TSTR_BUILDER_USE_REALLOC
struct TStringInternalControlBlock *tstr_internal_control_block_reallocate(
    struct TStringInternalControlBlock *cb TH_NONNULL, size_t bytes)
{
    return reinterpret_cast<struct TStringInternalControlBlock *>(
        realloc(cb, sizeof(struct TStringInternalControlBlock) + bytes));
}
#endif

bool tstr_builder_reallocate_utf8(TStringBuilder *builder_ptr, size_t cap, size_t len)
{
#if TSTR_BUILDER_USE_REALLOC
    if (tstr_builder_mode(*builder_ptr) != TSTRING_STORAGE_INTERNAL) [[unlikely]] {
        return false;
    }
    (void)len;
    auto cb = tstr_internal_control_block_reallocate(builder_ptr->cb, (cap + 1) * sizeof(char));
    if (!cb) {
        return false;
    }
    char *buf = reinterpret_cast<char *>(cb + 1);
    *builder_ptr = tstr_builder_new_impl(TSTRING_ENCODING_UTF8, buf, cap * sizeof(char), cb);
#else
    TStringBuilder builder = tstr_builder_new_utf8(cap);
    if (!tstr_builder_is_valid(builder)) {
        return false;
    }
    size_t needed = std::min({tstr_builder_cap_utf8(*builder_ptr), len, cap});
    std::copy_n(tstr_builder_buf_utf8(*builder_ptr), needed, tstr_builder_mut_buf_utf8(builder));
    tstr_builder_drop(*builder_ptr);
    *builder_ptr = builder;
#endif
    return true;
}

bool tstr_builder_reallocate_utf16(TStringBuilder *builder_ptr, size_t cap, size_t len)
{
#if TSTR_BUILDER_USE_REALLOC
    if (tstr_builder_mode(*builder_ptr) != TSTRING_STORAGE_INTERNAL) [[unlikely]] {
        return false;
    }
    (void)len;
    auto cb = tstr_internal_control_block_reallocate(builder_ptr->cb, (cap + 1) * sizeof(uint16_t));
    if (!cb) {
        return false;
    }
    uint16_t *buf = reinterpret_cast<uint16_t *>(cb + 1);
    *builder_ptr = tstr_builder_new_impl(TSTRING_ENCODING_UTF16, buf, cap * sizeof(uint16_t), cb);
#else
    TStringBuilder builder = tstr_builder_new_utf16(cap);
    if (!tstr_builder_is_valid(builder)) {
        return false;
    }
    size_t needed = std::min({tstr_builder_cap_utf16(*builder_ptr), len, cap});
    std::copy_n(tstr_builder_buf_utf16(*builder_ptr), needed, tstr_builder_mut_buf_utf16(builder));
    tstr_builder_drop(*builder_ptr);
    *builder_ptr = builder;
#endif
    return true;
}

void tstr_builder_drop(TStringBuilder builder)
{
    if (tstr_builder_mode(builder) == TSTRING_STORAGE_INTERNAL) {
        tstr_internal_control_block_drop(builder.cb);
    }
}

TString tstr_builder_finish_utf8(TStringBuilder builder, size_t len)
{
    if (tstr_builder_mode(builder) != TSTRING_STORAGE_INTERNAL || len > tstr_builder_cap_utf8(builder)) [[unlikely]] {
        tstr_builder_drop(builder);
        return tstr_new_invalid();
    }

    tstr_builder_mut_buf_utf8(builder)[len] = '\0';
    return tstr_new_internal_impl(TSTRING_ENCODING_UTF8, tstr_builder_buf_utf8(builder), len * sizeof(char),
                                  builder.cb);
}

TString tstr_builder_finish_utf16(TStringBuilder builder, size_t len)
{
    if (tstr_builder_mode(builder) != TSTRING_STORAGE_INTERNAL || len > tstr_builder_cap_utf16(builder)) [[unlikely]] {
        tstr_builder_drop(builder);
        return tstr_new_invalid();
    }

    tstr_builder_mut_buf_utf16(builder)[len] = u'\0';
    return tstr_new_internal_impl(TSTRING_ENCODING_UTF16, tstr_builder_buf_utf16(builder), len * sizeof(uint16_t),
                                  builder.cb);
}

TString tstr_new_copied_utf8(char const *value TH_NONNULL, size_t len)
{
    TStringBuilder builder = tstr_builder_new_utf8(len);
    if (!tstr_builder_is_valid(builder)) [[unlikely]] {
        return tstr_new_invalid();
    }
    char *buf = tstr_builder_mut_buf_utf8(builder);
    char *end = std::copy_n(value, len, buf);
    return tstr_builder_finish_utf8(builder, end - buf);
}

TString tstr_new_copied_utf16(uint16_t const *value TH_NONNULL, size_t len)
{
    TStringBuilder builder = tstr_builder_new_utf16(len);
    if (!tstr_builder_is_valid(builder)) [[unlikely]] {
        return tstr_new_invalid();
    }
    uint16_t *buf = tstr_builder_mut_buf_utf16(builder);
    uint16_t *end = std::copy_n(value, len, buf);
    return tstr_builder_finish_utf16(builder, end - buf);
}

TString tstr_dup_as_utf16(TString tstr)
{
    uint32_t encoding = tstr_encoding(tstr);
    if (encoding == TSTRING_ENCODING_UTF16) {
        return tstr_dup(tstr);
    }
    size_t len = 0;
    if (encoding == TSTRING_ENCODING_UTF8) {
        len = count_utf8_to_utf16(tstr_buf_utf8(tstr), tstr_len_utf8(tstr));
    } else {
        return tstr_new_invalid();
    }
    TStringBuilder builder = tstr_builder_new_utf16(len);
    if (!tstr_builder_is_valid(builder)) [[unlikely]] {
        return tstr_new_invalid();
    }
    uint16_t *buf = tstr_builder_mut_buf_utf16(builder);
    uint16_t *end = buf;
    if (encoding == TSTRING_ENCODING_UTF8) {
        end = write_utf8_to_utf16(tstr_buf_utf8(tstr), tstr_len_utf8(tstr), buf);
    }
    return tstr_builder_finish_utf16(builder, end - buf);
}

TString tstr_dup_as_utf8(TString tstr)
{
    uint32_t encoding = tstr_encoding(tstr);
    if (encoding == TSTRING_ENCODING_UTF8) {
        return tstr_dup(tstr);
    }
    size_t len = 0;
    if (encoding == TSTRING_ENCODING_UTF16) {
        len = count_utf16_to_utf8(tstr_buf_utf16(tstr), tstr_len_utf16(tstr));
    } else {
        return tstr_new_invalid();
    }
    TStringBuilder builder = tstr_builder_new_utf8(len);
    if (!tstr_builder_is_valid(builder)) [[unlikely]] {
        return tstr_new_invalid();
    }
    char *buf = tstr_builder_mut_buf_utf8(builder);
    char *end = buf;
    if (encoding == TSTRING_ENCODING_UTF16) {
        end = write_utf16_to_utf8(tstr_buf_utf16(tstr), tstr_len_utf16(tstr), buf);
    }
    return tstr_builder_finish_utf8(builder, end - buf);
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
            len += count_utf16_to_utf8(tstr_buf_utf16(tstr), tstr_len_utf16(tstr));
        } else {
            return tstr_new_invalid();
        }
    }
    TStringBuilder builder = tstr_builder_new_utf8(len);
    if (!tstr_builder_is_valid(builder)) [[unlikely]] {
        return tstr_new_invalid();
    }
    char *buf = tstr_builder_mut_buf_utf8(builder);
    char *end = buf;
    for (size_t i = 0; i < count; ++i) {
        TString tstr = tstr_list[i];
        uint32_t encoding = tstr_encoding(tstr);
        if (encoding == TSTRING_ENCODING_UTF8) {
            end = std::copy_n(tstr_buf_utf8(tstr), tstr_len_utf8(tstr), end);
        } else if (encoding == TSTRING_ENCODING_UTF16) {
            end = write_utf16_to_utf8(tstr_buf_utf16(tstr), tstr_len_utf16(tstr), end);
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
            len += count_utf8_to_utf16(tstr_buf_utf8(tstr), tstr_len_utf8(tstr));
        } else {
            return tstr_new_invalid();
        }
    }
    TStringBuilder builder = tstr_builder_new_utf16(len);
    if (!tstr_builder_is_valid(builder)) [[unlikely]] {
        return tstr_new_invalid();
    }
    uint16_t *buf = tstr_builder_mut_buf_utf16(builder);
    uint16_t *end = buf;
    for (size_t i = 0; i < count; ++i) {
        TString tstr = tstr_list[i];
        uint32_t encoding = tstr_encoding(tstr);
        if (encoding == TSTRING_ENCODING_UTF16) {
            end = std::copy_n(tstr_buf_utf16(tstr), tstr_len_utf16(tstr), end);
        } else if (encoding == TSTRING_ENCODING_UTF8) {
            end = write_utf8_to_utf16(tstr_buf_utf8(tstr), tstr_len_utf8(tstr), end);
        }
    }
    return tstr_builder_finish_utf16(builder, end - buf);
}
