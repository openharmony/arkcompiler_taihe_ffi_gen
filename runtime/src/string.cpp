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
#include <taihe/common.hpp>

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <stdexcept>

namespace {
constexpr uint32_t UNICODE_REPLACEMENT_CHAR = 0xfffd;

constexpr uint32_t UTF8_ASCII_END = 0x80;
constexpr uint32_t UTF8_TWO_BYTE_END = 0x800;
constexpr uint32_t UTF8_THREE_BYTE_END = 0x10000;
constexpr uint32_t UTF8_FOUR_BYTE_END = 0x110000;
constexpr uint32_t UTF16_SURROGATE_BEG = 0xd800;
constexpr uint32_t UTF16_SURROGATE_END = 0xe000;

constexpr uint8_t UTF8_ASCII_PREFIX_MASK = 0b10000000;
constexpr uint8_t UTF8_ASCII_PREFIX = 0b00000000;
constexpr uint8_t UTF8_ASCII_MASK = 0b01111111;
constexpr uint8_t UTF8_TWO_BYTE_PREFIX_MASK = 0b11100000;
constexpr uint8_t UTF8_TWO_BYTE_PREFIX = 0b11000000;
constexpr uint8_t UTF8_TWO_BYTE_MASK = 0b00011111;
constexpr uint8_t UTF8_THREE_BYTE_PREFIX_MASK = 0b11110000;
constexpr uint8_t UTF8_THREE_BYTE_PREFIX = 0b11100000;
constexpr uint8_t UTF8_THREE_BYTE_MASK = 0b00001111;
constexpr uint8_t UTF8_FOUR_BYTE_PREFIX_MASK = 0b11111000;
constexpr uint8_t UTF8_FOUR_BYTE_PREFIX = 0b11110000;
constexpr uint8_t UTF8_FOUR_BYTE_MASK = 0b00000111;
constexpr uint8_t UTF8_CONTINUATION_PREFIX_MASK = 0b11000000;
constexpr uint8_t UTF8_CONTINUATION_PREFIX = 0b10000000;
constexpr uint8_t UTF8_CONTINUATION_MASK = 0b00111111;

constexpr size_t UTF8_0_SHIFT = 0;
constexpr size_t UTF8_1_SHIFT = 6;
constexpr size_t UTF8_2_SHIFT = 12;
constexpr size_t UTF8_3_SHIFT = 18;

constexpr uint16_t UTF16_SURROGATE_PREFIX_MASK = 0xf800;
constexpr uint16_t UTF16_SURROGATE_PREFIX = 0xd800;
constexpr uint16_t UTF16_SURROGATE_HI_PREFIX_MASK = 0xfc00;
constexpr uint16_t UTF16_SURROGATE_HI_PREFIX = 0xd800;
constexpr uint16_t UTF16_SURROGATE_HI_MASK = 0x3ff;
constexpr uint16_t UTF16_SURROGATE_LO_PREFIX_MASK = 0xfc00;
constexpr uint16_t UTF16_SURROGATE_LO_PREFIX = 0xdc00;
constexpr uint16_t UTF16_SURROGATE_LO_MASK = 0x3ff;

constexpr size_t UTF16_SURROGATE_SHIFT_HI = 10;
constexpr size_t UTF16_SURROGATE_SHIFT_LO = 0;

struct utf8_encoding {
    static constexpr uint32_t encoding_flag = TSTRING_ENCODING_UTF8;

    using code_unit_type = char;

    template<typename Source>
    struct decoder {
        template<typename... Args>
        explicit decoder(Args &&...args) : src_(std::forward<Args>(args)...)
        {
        }

        bool done() const
        {
            return src_.done();
        }

        uint32_t decode()
        {
            uint8_t byte = read();
            if ((byte & UTF8_ASCII_PREFIX_MASK) == UTF8_ASCII_PREFIX) {
                uint32_t codepoint = 0;
                codepoint |= uint32_t(byte & UTF8_ASCII_MASK) << UTF8_0_SHIFT;
                return codepoint;
            }
            if ((byte & UTF8_TWO_BYTE_PREFIX_MASK) == UTF8_TWO_BYTE_PREFIX) {
                uint32_t codepoint = 0;
                codepoint |= uint32_t(byte & UTF8_TWO_BYTE_MASK) << UTF8_1_SHIFT;
                if (done() || (peek() & UTF8_CONTINUATION_PREFIX_MASK) != UTF8_CONTINUATION_PREFIX) {
                    return UNICODE_REPLACEMENT_CHAR;
                }
                codepoint |= uint32_t(read() & UTF8_CONTINUATION_MASK) << UTF8_0_SHIFT;
                if (codepoint < UTF8_ASCII_END || codepoint >= UTF8_TWO_BYTE_END) {
                    return UNICODE_REPLACEMENT_CHAR;
                }
                return codepoint;
            }
            if ((byte & UTF8_THREE_BYTE_PREFIX_MASK) == UTF8_THREE_BYTE_PREFIX) {
                uint32_t codepoint = 0;
                codepoint |= uint32_t(byte & UTF8_THREE_BYTE_MASK) << UTF8_2_SHIFT;
                if (done() || (peek() & UTF8_CONTINUATION_PREFIX_MASK) != UTF8_CONTINUATION_PREFIX) {
                    return UNICODE_REPLACEMENT_CHAR;
                }
                codepoint |= uint32_t(read() & UTF8_CONTINUATION_MASK) << UTF8_1_SHIFT;
                if (done() || (peek() & UTF8_CONTINUATION_PREFIX_MASK) != UTF8_CONTINUATION_PREFIX) {
                    return UNICODE_REPLACEMENT_CHAR;
                }
                codepoint |= uint32_t(read() & UTF8_CONTINUATION_MASK) << UTF8_0_SHIFT;
                if (codepoint < UTF8_TWO_BYTE_END || codepoint >= UTF8_THREE_BYTE_END ||
                    (codepoint >= UTF16_SURROGATE_BEG && codepoint < UTF16_SURROGATE_END)) {
                    return UNICODE_REPLACEMENT_CHAR;
                }
                return codepoint;
            }
            if ((byte & UTF8_FOUR_BYTE_PREFIX_MASK) == UTF8_FOUR_BYTE_PREFIX) {
                uint32_t codepoint = 0;
                codepoint |= uint32_t(byte & UTF8_FOUR_BYTE_MASK) << UTF8_3_SHIFT;
                if (done() || (peek() & UTF8_CONTINUATION_PREFIX_MASK) != UTF8_CONTINUATION_PREFIX) {
                    return UNICODE_REPLACEMENT_CHAR;
                }
                codepoint |= uint32_t(read() & UTF8_CONTINUATION_MASK) << UTF8_2_SHIFT;
                if (done() || (peek() & UTF8_CONTINUATION_PREFIX_MASK) != UTF8_CONTINUATION_PREFIX) {
                    return UNICODE_REPLACEMENT_CHAR;
                }
                codepoint |= uint32_t(read() & UTF8_CONTINUATION_MASK) << UTF8_1_SHIFT;
                if (done() || (peek() & UTF8_CONTINUATION_PREFIX_MASK) != UTF8_CONTINUATION_PREFIX) {
                    return UNICODE_REPLACEMENT_CHAR;
                }
                codepoint |= uint32_t(read() & UTF8_CONTINUATION_MASK) << UTF8_0_SHIFT;
                if (codepoint < UTF8_THREE_BYTE_END || codepoint >= UTF8_FOUR_BYTE_END) {
                    return UNICODE_REPLACEMENT_CHAR;
                }
                return codepoint;
            }
            return UNICODE_REPLACEMENT_CHAR;
        }

    private:
        Source src_;

        uint8_t read()
        {
            return uint8_t(src_.read());
        }

        uint8_t peek() const
        {
            return uint8_t(src_.peek());
        }
    };

    template<typename Sink>
    struct encoder {
        template<typename... Args>
        explicit encoder(Args &&...args) : sink_(std::forward<Args>(args)...)
        {
        }

        void encode(uint32_t codepoint)
        {
            if (codepoint < UTF8_ASCII_END) {
                push((uint8_t(codepoint >> UTF8_0_SHIFT) & UTF8_ASCII_MASK) | UTF8_ASCII_PREFIX);
            } else if (codepoint < UTF8_TWO_BYTE_END) {
                push((uint8_t(codepoint >> UTF8_1_SHIFT) & UTF8_TWO_BYTE_MASK) | UTF8_TWO_BYTE_PREFIX);
                push((uint8_t(codepoint >> UTF8_0_SHIFT) & UTF8_CONTINUATION_MASK) | UTF8_CONTINUATION_PREFIX);
            } else if (codepoint < UTF8_THREE_BYTE_END) {
                push((uint8_t(codepoint >> UTF8_2_SHIFT) & UTF8_THREE_BYTE_MASK) | UTF8_THREE_BYTE_PREFIX);
                push((uint8_t(codepoint >> UTF8_1_SHIFT) & UTF8_CONTINUATION_MASK) | UTF8_CONTINUATION_PREFIX);
                push((uint8_t(codepoint >> UTF8_0_SHIFT) & UTF8_CONTINUATION_MASK) | UTF8_CONTINUATION_PREFIX);
            } else {
                push((uint8_t(codepoint >> UTF8_3_SHIFT) & UTF8_FOUR_BYTE_MASK) | UTF8_FOUR_BYTE_PREFIX);
                push((uint8_t(codepoint >> UTF8_2_SHIFT) & UTF8_CONTINUATION_MASK) | UTF8_CONTINUATION_PREFIX);
                push((uint8_t(codepoint >> UTF8_1_SHIFT) & UTF8_CONTINUATION_MASK) | UTF8_CONTINUATION_PREFIX);
                push((uint8_t(codepoint >> UTF8_0_SHIFT) & UTF8_CONTINUATION_MASK) | UTF8_CONTINUATION_PREFIX);
            }
        }

        Sink sink()
        {
            return sink_;
        }

    private:
        Sink sink_;

        void push(uint8_t byte)
        {
            sink_.push(char(byte));
        }
    };
};

struct utf16_encoding {
    static constexpr uint32_t encoding_flag = TSTRING_ENCODING_UTF16;

    using code_unit_type = uint16_t;

    template<typename Source>
    struct decoder {
        template<typename... Args>
        explicit decoder(Args &&...args) : src_(std::forward<Args>(args)...)
        {
        }

        bool done() const
        {
            return src_.done();
        }

        uint32_t decode()
        {
            uint16_t unit = read();
            if ((unit & UTF16_SURROGATE_PREFIX_MASK) != UTF16_SURROGATE_PREFIX) {
                return uint32_t(unit);
            }
            if ((unit & UTF16_SURROGATE_HI_PREFIX_MASK) == UTF16_SURROGATE_HI_PREFIX && !done() &&
                (peek() & UTF16_SURROGATE_LO_PREFIX_MASK) == UTF16_SURROGATE_LO_PREFIX) {
                uint16_t next = read();
                return ((uint32_t(unit & UTF16_SURROGATE_HI_MASK) << UTF16_SURROGATE_SHIFT_HI) |
                        (uint32_t(next & UTF16_SURROGATE_LO_MASK) << UTF16_SURROGATE_SHIFT_LO)) +
                       UTF8_THREE_BYTE_END;
            }
            return UNICODE_REPLACEMENT_CHAR;
        }

    private:
        Source src_;

        uint16_t read()
        {
            return src_.read();
        }

        uint16_t peek() const
        {
            return src_.peek();
        }
    };

    template<typename Sink>
    struct encoder {
        template<typename... Args>
        explicit encoder(Args &&...args) : sink_(std::forward<Args>(args)...)
        {
        }

        void encode(uint32_t codepoint)
        {
            if (codepoint < UTF8_THREE_BYTE_END) {
                push(uint16_t(codepoint));
            } else {
                uint32_t surrogate = codepoint - UTF8_THREE_BYTE_END;
                push((uint16_t(surrogate >> UTF16_SURROGATE_SHIFT_HI) & UTF16_SURROGATE_HI_MASK) |
                     UTF16_SURROGATE_HI_PREFIX);
                push((uint16_t(surrogate >> UTF16_SURROGATE_SHIFT_LO) & UTF16_SURROGATE_LO_MASK) |
                     UTF16_SURROGATE_LO_PREFIX);
            }
        }

        Sink sink()
        {
            return sink_;
        }

    private:
        Sink sink_;

        void push(uint16_t unit)
        {
            sink_.push(unit);
        }
    };
};

template<typename Encoding>
constexpr uint32_t encoding_flag = Encoding::encoding_flag;

template<typename Encoding>
using code_unit_t = typename Encoding::code_unit_type;
}  // namespace

TH_INLINE void tstr_set_data(TString *tstr_ptr, void const *data)
{
    tstr_ptr->data = data;
}

TH_INLINE void tstr_set_byte_length(TString *tstr_ptr, size_t byte_length)
{
    tstr_ptr->byte_length = byte_length;
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

template<typename Encoding>
void tstr_set_buf(TString *tstr_ptr, code_unit_t<Encoding> const *buf)
{
    tstr_set_data(tstr_ptr, buf);
}

template<typename Encoding>
void tstr_set_len(TString *tstr_ptr, size_t len)
{
    tstr_set_byte_length(tstr_ptr, len * sizeof(code_unit_t<Encoding>));
}

template<typename Encoding>
code_unit_t<Encoding> const *tstr_buf(TString tstr)
{
    return reinterpret_cast<code_unit_t<Encoding> const *>(tstr_data(tstr));
}

template<typename Encoding>
size_t tstr_len(TString tstr)
{
    return tstr_byte_length(tstr) / sizeof(code_unit_t<Encoding>);
}

template<typename Encoding>
TString tstr_new_static(code_unit_t<Encoding> const *buf TH_NONNULL, size_t len)
{
    TString tstr;
    tstr.flags = TSTRING_STORAGE_STATIC | (encoding_flag<Encoding> & TSTRING_ENCODING_MASK);
    tstr_set_buf<Encoding>(&tstr, buf);
    tstr_set_len<Encoding>(&tstr, len);
    return tstr;
}

TString tstr_new_static_utf8(char const *buf TH_NONNULL, size_t len)
{
    return tstr_new_static<utf8_encoding>(buf, len);
}

TString tstr_new_static_utf16(uint16_t const *buf TH_NONNULL, size_t len)
{
    return tstr_new_static<utf16_encoding>(buf, len);
}

TH_INLINE TString tstr_new_internal_raw(uint32_t encoding, void const *data TH_NONNULL, size_t byte_length,
                                        struct TStringInternalControlBlock *cb TH_NONNULL)
{
    TString tstr;
    tstr.flags = TSTRING_STORAGE_INTERNAL | (encoding & TSTRING_ENCODING_MASK);
    tstr_set_data(&tstr, data);
    tstr_set_byte_length(&tstr, byte_length);
    tstr.internal_cb = cb;
    return tstr;
}

TH_INLINE TString tstr_new_acquired_raw(uint32_t encoding, void const *data TH_NONNULL, size_t byte_length,
                                        struct TStringAcquiredControlBlock *cb TH_NONNULL)
{
    TString tstr;
    tstr.flags = TSTRING_STORAGE_ACQUIRED | (encoding & TSTRING_ENCODING_MASK);
    tstr_set_data(&tstr, data);
    tstr_set_byte_length(&tstr, byte_length);
    tstr.acquired_cb = cb;
    return tstr;
}

TH_INLINE void tstr_global_context_release(struct TStringGlobalRefContext ctx)
{
    ctx.release(ctx.ref);
}

TH_INLINE struct TStringAcquiredControlBlock *tstr_acquired_control_block_new(struct TStringGlobalRefContext ctx)
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

template<typename Encoding>
TString tstr_new_acquired(code_unit_t<Encoding> const *buf TH_NONNULL, size_t len, struct TStringGlobalRefContext ctx)
{
    auto cb = tstr_acquired_control_block_new(ctx);
    if (!cb) {
        return tstr_new_invalid();
    }
    return tstr_new_acquired_raw(encoding_flag<Encoding>, buf, len * sizeof(code_unit_t<Encoding>), cb);
}

TString tstr_new_acquired_utf8(char const *buf TH_NONNULL, size_t len, struct TStringGlobalRefContext ctx)
{
    return tstr_new_acquired<utf8_encoding>(buf, len, ctx);
}

TString tstr_new_acquired_utf16(uint16_t const *buf TH_NONNULL, size_t len, struct TStringGlobalRefContext ctx)
{
    return tstr_new_acquired<utf16_encoding>(buf, len, ctx);
}

TH_INLINE void tstr_acquire_cache_init(struct TStringAcquireCache *cache TH_NONNULL, struct TStringLocalRefContext ctx)
{
    cache->acquired_cb = nullptr;
    cache->local_ctx = ctx;
}

template<typename Encoding>
TString tstr_new_acquirable_borrowed(code_unit_t<Encoding> const *buf TH_NONNULL, size_t len,
                                     struct TStringAcquireCache *cache TH_NONNULL, struct TStringLocalRefContext ctx)
{
    TString tstr;
    tstr.flags = TSTRING_STORAGE_ACQUIRABLE_BORROWED | (encoding_flag<Encoding> & TSTRING_ENCODING_MASK);
    tstr_set_buf<Encoding>(&tstr, buf);
    tstr_set_len<Encoding>(&tstr, len);
    tstr.acquire_cache = cache;
    tstr_acquire_cache_init(cache, ctx);
    return tstr;
}

TString tstr_new_acquirable_borrowed_utf8(char const *buf TH_NONNULL, size_t len,
                                          struct TStringAcquireCache *cache TH_NONNULL,
                                          struct TStringLocalRefContext ctx)
{
    return tstr_new_acquirable_borrowed<utf8_encoding>(buf, len, cache, ctx);
}

TString tstr_new_acquirable_borrowed_utf16(uint16_t const *buf TH_NONNULL, size_t len,
                                           struct TStringAcquireCache *cache TH_NONNULL,
                                           struct TStringLocalRefContext ctx)
{
    return tstr_new_acquirable_borrowed<utf16_encoding>(buf, len, cache, ctx);
}

TH_INLINE void tstr_copy_cache_init(struct TStringCopyCache *cache, TString original)
{
    if (cache == nullptr) {
        return;
    }
    cache->copied = tstr_new_invalid();
    cache->original = original;
}

template<typename Encoding>
TString tstr_new_copyable_borrowed(code_unit_t<Encoding> const *buf TH_NONNULL, size_t len,
                                   struct TStringCopyCache *cache)
{
    TString tstr;
    tstr.flags = TSTRING_STORAGE_COPIABLE_BORROWED | (encoding_flag<Encoding> & TSTRING_ENCODING_MASK);
    tstr_set_buf<Encoding>(&tstr, buf);
    tstr_set_len<Encoding>(&tstr, len);
    tstr.copy_cache = cache;
    tstr_copy_cache_init(cache, tstr);
    return tstr;
}

TString tstr_new_copyable_borrowed_utf8(char const *buf TH_NONNULL, size_t len, struct TStringCopyCache *cache)
{
    return tstr_new_copyable_borrowed<utf8_encoding>(buf, len, cache);
}

TString tstr_new_copyable_borrowed_utf16(uint16_t const *buf TH_NONNULL, size_t len, struct TStringCopyCache *cache)
{
    return tstr_new_copyable_borrowed<utf16_encoding>(buf, len, cache);
}

TH_INLINE TString tstr_substr_raw(uint32_t encoding, TString tstr, size_t byte_offset, size_t byte_length)
{
    tstr.flags = (tstr.flags & ~TSTRING_ENCODING_MASK) | (encoding & TSTRING_ENCODING_MASK);
    tstr_set_data(&tstr, reinterpret_cast<std::byte const *>(tstr_data(tstr)) + byte_offset);
    tstr_set_byte_length(&tstr, byte_length);
    return tstr;
}

template<typename Encoding>
TString tstr_substr(TString tstr, size_t pos, size_t len, struct TStringCopyCache *cache)
{
    if (!tstr_is_valid(tstr)) {
        tstr_copy_cache_init(cache, tstr_new_invalid());
        return tstr_new_invalid();
    }
    size_t len_original = tstr_len<Encoding>(tstr);
    if (pos > len_original) {
        tstr_copy_cache_init(cache, tstr_new_invalid());
        return tstr_new_invalid();
    }
    size_t len_remaining = len_original - pos;
    if (len > len_remaining) {
        len = len_remaining;
    }
#if TSTR_ENABLE_RETAINABLE_SUBSTR
    uint32_t mode = tstr_mode(tstr);
    if (mode != TSTRING_STORAGE_COPIABLE_BORROWED || tstr.copy_cache != nullptr) {
        tstr_copy_cache_init(cache, tstr_new_invalid());
        return tstr_substr_raw(encoding_flag<Encoding>, tstr, pos * sizeof(code_unit_t<Encoding>),
                               len * sizeof(code_unit_t<Encoding>));
    }
#endif
    return tstr_new_copyable_borrowed<Encoding>(tstr_buf<Encoding>(tstr) + pos, len, cache);
}

TString tstr_substr_utf8(TString tstr, size_t pos, size_t len, struct TStringCopyCache *cache)
{
    return tstr_substr<utf8_encoding>(tstr, pos, len, cache);
}

TString tstr_substr_utf16(TString tstr, size_t pos, size_t len, struct TStringCopyCache *cache)
{
    return tstr_substr<utf16_encoding>(tstr, pos, len, cache);
}

TH_INLINE struct TStringGlobalRefContext tstr_local_context_acquire(struct TStringLocalRefContext ctx)
{
    return ctx.acquire(ctx.ref);
}

TH_INLINE TString tstr_acquire_cache_get_relative(uint32_t encoding, void const *data TH_NONNULL, size_t byte_length,
                                                  struct TStringAcquireCache *cache TH_NONNULL)
{
    if (cache->acquired_cb == nullptr) {
        struct TStringGlobalRefContext ctx = tstr_local_context_acquire(cache->local_ctx);
        cache->acquired_cb = tstr_acquired_control_block_new(ctx);
        if (cache->acquired_cb == nullptr) {
            return tstr_new_invalid();
        }
    }
    return tstr_new_acquired_raw(encoding, data, byte_length, cache->acquired_cb);
}

TH_INLINE TString tstr_copy(TString tstr)
{
    switch (tstr_encoding(tstr)) {
        case TSTRING_ENCODING_UTF8:
            return tstr_new_copied_utf8(tstr_buf_utf8(tstr), tstr_len_utf8(tstr));
        case TSTRING_ENCODING_UTF16:
            return tstr_new_copied_utf16(tstr_buf_utf16(tstr), tstr_len_utf16(tstr));
        default:
            return tstr_new_invalid();
    }
}

TH_INLINE TString tstr_copy_cache_get_relative(uint32_t encoding, void const *data TH_NONNULL, size_t byte_length,
                                               struct TStringCopyCache *cache TH_NONNULL)
{
    if (!tstr_is_valid(cache->copied)) {
        cache->copied = tstr_copy(cache->original);
        if (!tstr_is_valid(cache->copied)) {
            return tstr_new_invalid();
        }
    }
    return tstr_substr_raw(
        encoding, cache->copied,
        reinterpret_cast<std::byte const *>(data) - reinterpret_cast<std::byte const *>(tstr_data(cache->original)),
        byte_length);
}

TH_INLINE struct TStringInternalControlBlock *tstr_internal_control_block_dup(
    struct TStringInternalControlBlock *cb TH_NONNULL)
{
    tref_inc(&cb->ref_count);
    return cb;
}

TH_INLINE struct TStringAcquiredControlBlock *tstr_acquired_control_block_dup(
    struct TStringAcquiredControlBlock *cb TH_NONNULL)
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
        return tstr_new_internal_raw(tstr_encoding(tstr), tstr_data(tstr), tstr_byte_length(tstr),
                                     tstr_internal_control_block_dup(tstr.internal_cb));
    }
    if (mode == TSTRING_STORAGE_ACQUIRED) {
        return tstr_new_acquired_raw(tstr_encoding(tstr), tstr_data(tstr), tstr_byte_length(tstr),
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

TH_INLINE void tstr_internal_control_block_drop(struct TStringInternalControlBlock *cb TH_NONNULL)
{
    if (tref_dec(&cb->ref_count)) {
        free(cb);
    }
}

TH_INLINE void tstr_acquired_control_block_drop(struct TStringAcquiredControlBlock *cb TH_NONNULL)
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
constexpr size_t HASH_SEED = 0x9e3779b9;
constexpr size_t HASH_SHIFT_LEFT = 6;
constexpr size_t HASH_SHIFT_RIGHT = 2;

template<typename Decoder>
size_t hash_decoded(Decoder decoder)
{
    size_t hash = 0;
    while (!decoder.done()) {
        uint32_t codepoint = decoder.decode();
        hash ^= codepoint + HASH_SEED + (hash << HASH_SHIFT_LEFT) + (hash >> HASH_SHIFT_RIGHT);
    }
    return hash;
}

template<typename LeftDecoder, typename RightDecoder>
int compare_decoded(LeftDecoder ldec, RightDecoder rdec)
{
    while (!ldec.done() && !rdec.done()) {
        uint32_t lcode = ldec.decode();
        uint32_t rcode = rdec.decode();
        if (lcode < rcode) {
            return -1;
        }
        if (lcode > rcode) {
            return 1;
        }
    }
    if (!ldec.done()) {
        return 1;
    }
    if (!rdec.done()) {
        return -1;
    }
    return 0;
}

template<typename Decoder, typename Encoder>
Encoder transcode(Decoder decoder, Encoder encoder)
{
    while (!decoder.done()) {
        encoder.encode(decoder.decode());
    }
    return encoder;
}

template<typename Encoding, typename Source>
auto source_to_decoder(Source source)
{
    return typename Encoding::template decoder<Source>(source);
}

template<typename Unit>
struct read_source {
    explicit read_source(Unit const *pos, Unit const *end) : pos_(pos), end_(end)
    {
    }

    bool done() const
    {
        return pos_ == end_;
    }

    Unit read()
    {
        return *pos_++;
    }

    Unit peek() const
    {
        return *pos_;
    }

private:
    Unit const *pos_;
    Unit const *end_;
};

template<typename Encoding>
auto tstr_to_decoder(TString tstr)
{
    code_unit_t<Encoding> const *buf = tstr_buf<Encoding>(tstr);
    code_unit_t<Encoding> const *end = buf + tstr_len<Encoding>(tstr);
    return source_to_decoder<Encoding>(read_source<code_unit_t<Encoding>>(buf, end));
}

template<typename Encoding, typename Sink>
auto sink_to_encoder(Sink sink)
{
    return typename Encoding::template encoder<Sink>(sink);
}

template<typename FromEncoding, typename ToEncoding, typename Sink>
auto tstr_transcode(TString tstr, Sink sink)
{
    return transcode(tstr_to_decoder<FromEncoding>(tstr), sink_to_encoder<ToEncoding>(sink)).sink();
}

template<typename Unit>
struct count_sink {
    explicit count_sink(size_t count) : count_(count)
    {
    }

    void push(Unit)
    {
        count_++;
    }

    size_t count()
    {
        return count_;
    }

private:
    size_t count_;
};

template<typename FromEncoding, typename ToEncoding>
auto tstr_count_transcoded(TString tstr)
{
    return tstr_transcode<FromEncoding, ToEncoding>(tstr, count_sink<code_unit_t<ToEncoding>>(0)).count();
}

template<typename Unit>
struct write_sink {
    explicit write_sink(Unit *pos) : pos_(pos)
    {
    }

    void push(Unit value)
    {
        *pos_++ = value;
    }

    Unit *pos()
    {
        return pos_;
    }

private:
    Unit *pos_;
};

template<typename FromEncoding, typename ToEncoding>
auto tstr_write_transcoded(TString tstr, code_unit_t<ToEncoding> *pos)
{
    return tstr_transcode<FromEncoding, ToEncoding>(tstr, write_sink<code_unit_t<ToEncoding>>(pos)).pos();
}
}  // namespace

template<typename Decoder>
int tstr_compare_impl(Decoder ldec, TString rstr)
{
    switch (tstr_encoding(rstr)) {
        case TSTRING_ENCODING_UTF8:
            return compare_decoded(ldec, tstr_to_decoder<utf8_encoding>(rstr));
        case TSTRING_ENCODING_UTF16:
            return compare_decoded(ldec, tstr_to_decoder<utf16_encoding>(rstr));
        default:
            TH_THROW(std::invalid_argument, "Unsupported encoding");
    }
}

int tstr_compare(TString lstr, TString rstr)
{
    switch (tstr_encoding(lstr)) {
        case TSTRING_ENCODING_UTF8:
            return tstr_compare_impl(tstr_to_decoder<utf8_encoding>(lstr), rstr);
        case TSTRING_ENCODING_UTF16:
            return tstr_compare_impl(tstr_to_decoder<utf16_encoding>(lstr), rstr);
        default:
            TH_THROW(std::invalid_argument, "Unsupported encoding");
    }
}

size_t tstr_hash(TString tstr)
{
    switch (tstr_encoding(tstr)) {
        case TSTRING_ENCODING_UTF8:
            return hash_decoded(tstr_to_decoder<utf8_encoding>(tstr));
        case TSTRING_ENCODING_UTF16:
            return hash_decoded(tstr_to_decoder<utf16_encoding>(tstr));
        default:
            TH_THROW(std::invalid_argument, "Unsupported encoding");
    }
}

TH_INLINE void tstr_builder_set_buffer(TStringBuilder *builder_ptr, void *data)
{
    builder_ptr->buffer = data;
}

TH_INLINE void tstr_builder_set_byte_capacity(TStringBuilder *builder_ptr, size_t byte_capacity)
{
    builder_ptr->byte_capacity = byte_capacity;
}

TH_INLINE uint32_t tstr_builder_mode(TStringBuilder builder)
{
    return builder.flags & TSTRING_STORAGE_MASK;
}

TH_INLINE uint32_t tstr_builder_is_valid(TStringBuilder builder)
{
    return tstr_builder_mode(builder) != TSTRING_STORAGE_INVALID;
}

template<typename Encoding>
void tstr_builder_set_buf(TStringBuilder *builder_ptr, code_unit_t<Encoding> *buf)
{
    tstr_builder_set_buffer(builder_ptr, buf);
}

template<typename Encoding>
void tstr_builder_set_cap(TStringBuilder *builder_ptr, size_t cap)
{
    tstr_builder_set_byte_capacity(builder_ptr, cap * sizeof(code_unit_t<Encoding>));
}

template<typename Encoding>
code_unit_t<Encoding> const *tstr_builder_buf(TStringBuilder builder)
{
    return reinterpret_cast<code_unit_t<Encoding> const *>(tstr_builder_buffer(builder));
}

template<typename Encoding>
code_unit_t<Encoding> *tstr_builder_mut_buf(TStringBuilder builder)
{
    return reinterpret_cast<code_unit_t<Encoding> *>(tstr_builder_mut_buffer(builder));
}

template<typename Encoding>
size_t tstr_builder_cap(TStringBuilder builder)
{
    return tstr_builder_byte_capacity(builder) / sizeof(code_unit_t<Encoding>);
}

TStringBuilder tstr_builder_new_invalid()
{
    TStringBuilder builder;
    builder.flags = TSTRING_STORAGE_INVALID | TSTRING_ENCODING_UNKNOWN;
    tstr_builder_set_byte_capacity(&builder, 0);
    tstr_builder_set_buffer(&builder, nullptr);
    return builder;
}

TH_INLINE TStringBuilder tstr_builder_new_raw(uint32_t encoding, void *data, size_t byte_capacity,
                                              struct TStringInternalControlBlock *cb TH_NONNULL)
{
    TStringBuilder builder;
    builder.flags = TSTRING_STORAGE_INTERNAL | (encoding & TSTRING_ENCODING_MASK);
    tstr_builder_set_buffer(&builder, data);
    tstr_builder_set_byte_capacity(&builder, byte_capacity);
    builder.cb = cb;
    return builder;
}

TH_INLINE struct TStringInternalControlBlock *tstr_internal_control_block_new(size_t bytes)
{
    size_t required = sizeof(struct TStringInternalControlBlock) + bytes;
    auto cb = reinterpret_cast<struct TStringInternalControlBlock *>(malloc(required));
    if (!cb) {
        return nullptr;
    }
    tref_init(&cb->ref_count, 1);
    return cb;
}

template<typename Encoding>
TStringBuilder tstr_builder_new(size_t cap)
{
    auto cb = tstr_internal_control_block_new((cap + 1) * sizeof(code_unit_t<Encoding>));
    if (!cb) {
        return tstr_builder_new_invalid();
    }
    auto buf = reinterpret_cast<code_unit_t<Encoding> *>(cb + 1);
    return tstr_builder_new_raw(encoding_flag<Encoding>, buf, cap * sizeof(code_unit_t<Encoding>), cb);
}

TStringBuilder tstr_builder_new_utf8(size_t cap)
{
    return tstr_builder_new<utf8_encoding>(cap);
}

TStringBuilder tstr_builder_new_utf16(size_t cap)
{
    return tstr_builder_new<utf16_encoding>(cap);
}

#if TSTR_BUILDER_USE_REALLOC
TH_INLINE struct TStringInternalControlBlock *tstr_internal_control_block_reallocate(
    struct TStringInternalControlBlock *cb TH_NONNULL, size_t bytes)
{
    return reinterpret_cast<struct TStringInternalControlBlock *>(
        realloc(cb, sizeof(struct TStringInternalControlBlock) + bytes));
}
#endif

template<typename Encoding>
bool tstr_builder_reallocate(TStringBuilder *builder_ptr, size_t cap, size_t len)
{
#if TSTR_BUILDER_USE_REALLOC
    if (tstr_builder_mode(*builder_ptr) != TSTRING_STORAGE_INTERNAL) [[unlikely]] {
        return false;
    }
    (void)len;
    auto cb = tstr_internal_control_block_reallocate(builder_ptr->cb, (cap + 1) * sizeof(tstr_code_unit_t<Encoding>));
    if (!cb) {
        return false;
    }
    auto buf = reinterpret_cast<tstr_code_unit_t<Encoding> *>(cb + 1);
    *builder_ptr =
        tstr_builder_new_raw(tstr_encoding_flag<Encoding>, buf, cap * sizeof(tstr_code_unit_t<Encoding>), cb);
#else
    TStringBuilder builder = tstr_builder_new<Encoding>(cap);
    if (!tstr_builder_is_valid(builder)) {
        return false;
    }
    size_t needed = std::min({tstr_builder_cap<Encoding>(*builder_ptr), len, cap});
    std::copy_n(tstr_builder_buf<Encoding>(*builder_ptr), needed, tstr_builder_mut_buf<Encoding>(builder));
    tstr_builder_drop(*builder_ptr);
    *builder_ptr = builder;
#endif
    return true;
}

bool tstr_builder_reallocate_utf8(TStringBuilder *builder_ptr, size_t cap, size_t len)
{
    return tstr_builder_reallocate<utf8_encoding>(builder_ptr, cap, len);
}

bool tstr_builder_reallocate_utf16(TStringBuilder *builder_ptr, size_t cap, size_t len)
{
    return tstr_builder_reallocate<utf16_encoding>(builder_ptr, cap, len);
}

void tstr_builder_drop(TStringBuilder builder)
{
    if (tstr_builder_mode(builder) == TSTRING_STORAGE_INTERNAL) {
        tstr_internal_control_block_drop(builder.cb);
    }
}

template<typename Encoding>
TString tstr_builder_finish(TStringBuilder builder, size_t len)
{
    if (tstr_builder_mode(builder) != TSTRING_STORAGE_INTERNAL || len > tstr_builder_cap<Encoding>(builder))
        [[unlikely]] {
        tstr_builder_drop(builder);
        return tstr_new_invalid();
    }
    tstr_builder_mut_buf<Encoding>(builder)[len] = 0;
    return tstr_new_internal_raw(encoding_flag<Encoding>, tstr_builder_buf<Encoding>(builder),
                                 len * sizeof(code_unit_t<Encoding>), builder.cb);
}

TString tstr_builder_finish_utf8(TStringBuilder builder, size_t len)
{
    return tstr_builder_finish<utf8_encoding>(builder, len);
}

TString tstr_builder_finish_utf16(TStringBuilder builder, size_t len)
{
    return tstr_builder_finish<utf16_encoding>(builder, len);
}

template<typename Encoding>
TString tstr_new_copied(code_unit_t<Encoding> const *value TH_NONNULL, size_t len)
{
    TStringBuilder builder = tstr_builder_new<Encoding>(len);
    if (!tstr_builder_is_valid(builder)) [[unlikely]] {
        return tstr_new_invalid();
    }
    auto buf = tstr_builder_mut_buf<Encoding>(builder);
    auto end = std::copy_n(value, len, buf);
    return tstr_builder_finish<Encoding>(builder, end - buf);
}

TString tstr_new_copied_utf8(char const *value TH_NONNULL, size_t len)
{
    return tstr_new_copied<utf8_encoding>(value, len);
}

TString tstr_new_copied_utf16(uint16_t const *value TH_NONNULL, size_t len)
{
    return tstr_new_copied<utf16_encoding>(value, len);
}

template<typename Encoding>
TString tstr_dup_as(TString tstr)
{
    uint32_t encoding = tstr_encoding(tstr);
    if (encoding == encoding_flag<Encoding>) {
        return tstr_dup(tstr);
    }
    size_t len = 0;
    switch (encoding) {
        case TSTRING_ENCODING_UTF8:
            len += tstr_count_transcoded<utf8_encoding, Encoding>(tstr);
            break;
        case TSTRING_ENCODING_UTF16:
            len += tstr_count_transcoded<utf16_encoding, Encoding>(tstr);
            break;
        default:
            return tstr_new_invalid();
    }
    TStringBuilder builder = tstr_builder_new<Encoding>(len);
    if (!tstr_builder_is_valid(builder)) [[unlikely]] {
        return tstr_new_invalid();
    }
    code_unit_t<Encoding> *buf = tstr_builder_mut_buf<Encoding>(builder);
    code_unit_t<Encoding> *pos = buf;
    switch (encoding) {
        case TSTRING_ENCODING_UTF8:
            pos = tstr_write_transcoded<utf8_encoding, Encoding>(tstr, pos);
            break;
        case TSTRING_ENCODING_UTF16:
            pos = tstr_write_transcoded<utf16_encoding, Encoding>(tstr, pos);
            break;
    }
    return tstr_builder_finish<Encoding>(builder, pos - buf);
}

TString tstr_dup_as_utf8(TString tstr)
{
    return tstr_dup_as<utf8_encoding>(tstr);
}

TString tstr_dup_as_utf16(TString tstr)
{
    return tstr_dup_as<utf16_encoding>(tstr);
}

template<typename Encoding>
TString tstr_concat_as(size_t count, TString const *tstr_list)
{
    size_t len = 0;
    for (size_t i = 0; i < count; ++i) {
        TString tstr = tstr_list[i];
        uint32_t encoding = tstr_encoding(tstr);
        if (encoding == encoding_flag<Encoding>) {
            len += tstr_len<Encoding>(tstr);
        } else if (encoding == TSTRING_ENCODING_UTF8) {
            len += tstr_count_transcoded<utf8_encoding, Encoding>(tstr);
        } else if (encoding == TSTRING_ENCODING_UTF16) {
            len += tstr_count_transcoded<utf16_encoding, Encoding>(tstr);
        } else {
            return tstr_new_invalid();
        }
    }
    TStringBuilder builder = tstr_builder_new<Encoding>(len);
    if (!tstr_builder_is_valid(builder)) [[unlikely]] {
        return tstr_new_invalid();
    }
    code_unit_t<Encoding> *buf = tstr_builder_mut_buf<Encoding>(builder);
    code_unit_t<Encoding> *pos = buf;
    for (size_t i = 0; i < count; ++i) {
        TString tstr = tstr_list[i];
        uint32_t encoding = tstr_encoding(tstr);
        if (encoding == encoding_flag<Encoding>) {
            pos = std::copy_n(tstr_buf<Encoding>(tstr), tstr_len<Encoding>(tstr), pos);
        } else if (encoding == TSTRING_ENCODING_UTF8) {
            pos = tstr_write_transcoded<utf8_encoding, Encoding>(tstr, pos);
        } else if (encoding == TSTRING_ENCODING_UTF16) {
            pos = tstr_write_transcoded<utf16_encoding, Encoding>(tstr, pos);
        }
    }
    return tstr_builder_finish<Encoding>(builder, pos - buf);
}

TString tstr_concat_as_utf8(size_t count, TString const *tstr_list)
{
    return tstr_concat_as<utf8_encoding>(count, tstr_list);
}

TString tstr_concat_as_utf16(size_t count, TString const *tstr_list)
{
    return tstr_concat_as<utf16_encoding>(count, tstr_list);
}
