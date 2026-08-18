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

#include <algorithm>
#include <cstdint>

namespace {
constexpr size_t UTF8_FAST_WORD_SIZE = sizeof(uint64_t) / sizeof(uint8_t);
constexpr size_t UTF8_FAST_BLOCK_SIZE = UTF8_FAST_WORD_SIZE * 2;
constexpr size_t UTF16_FAST_WORD_SIZE = sizeof(uint64_t) / sizeof(uint16_t);
constexpr size_t UTF16_FAST_BLOCK_SIZE = UTF16_FAST_WORD_SIZE * 2;

constexpr size_t UTF8_ONE_BYTE_COUNT = 1;
constexpr size_t UTF8_TWO_BYTE_COUNT = 2;
constexpr size_t UTF8_THREE_BYTE_COUNT = 3;
constexpr size_t UTF8_FOUR_BYTE_COUNT = 4;

constexpr size_t UTF16_ONE_UNIT_COUNT = 1;
constexpr size_t UTF16_TWO_UNIT_COUNT = 2;

constexpr size_t UTF8_CONTINUATION_BYTE_OFFSET = 1;
constexpr size_t UTF8_THREE_BYTE_LAST_OFFSET = 2;
constexpr size_t UTF8_FOUR_BYTE_LAST_OFFSET = 3;

constexpr size_t UTF16_TRAIL_SURROGATE_OFFSET = 1;

constexpr uint8_t UTF8_NON_ASCII_MIN = 0b10000000;
constexpr uint8_t UTF8_TWO_BYTE_PREFIX_MASK = 0b11100000;
constexpr uint8_t UTF8_TWO_BYTE_PREFIX = 0b11000000;
constexpr uint8_t UTF8_THREE_BYTE_PREFIX_MASK = 0b11110000;
constexpr uint8_t UTF8_THREE_BYTE_PREFIX = 0b11100000;
constexpr uint8_t UTF8_FOUR_BYTE_PREFIX_MASK = 0b11111000;
constexpr uint8_t UTF8_FOUR_BYTE_PREFIX = 0b11110000;
constexpr uint8_t UTF8_CONTINUATION_MASK = 0b11000000;
constexpr uint8_t UTF8_CONTINUATION_PREFIX = 0b10000000;
constexpr uint8_t UTF8_PAYLOAD_MASK = 0b00111111;
constexpr uint8_t UTF8_TWO_BYTE_PAYLOAD_MASK = 0b00011111;
constexpr uint8_t UTF8_THREE_BYTE_PAYLOAD_MASK = 0b00001111;
constexpr uint8_t UTF8_FOUR_BYTE_PAYLOAD_MASK = 0b00000111;

constexpr uint32_t UTF8_TWO_BYTE_MIN = 0x80;
constexpr uint32_t UTF8_TWO_BYTE_MAX = 0x7ff;
constexpr uint32_t UTF8_THREE_BYTE_MIN = 0x800;
constexpr uint32_t UTF8_THREE_BYTE_MAX = 0xffff;
constexpr uint32_t UTF8_FOUR_BYTE_MIN = 0x10000;
constexpr uint32_t UTF8_FOUR_BYTE_MAX = 0x10ffff;
constexpr uint32_t UTF16_SURROGATE_HIGH_START = 0xd800;
constexpr uint32_t UTF16_SURROGATE_LOW_START = 0xdc00;
constexpr uint32_t UTF16_SURROGATE_LOW_END = 0xdfff;
constexpr uint32_t UTF16_SURROGATE_MASK = 0x3ff;

constexpr uint32_t UTF8_SHIFT_1 = 6;
constexpr uint32_t UTF8_SHIFT_2 = 12;
constexpr uint32_t UTF8_SHIFT_3 = 18;
constexpr uint32_t UTF16_SURROGATE_SHIFT = 10;

constexpr uint16_t UNICODE_REPLACEMENT_CHAR = 0xfffd;
constexpr uint8_t UTF8_REPLACEMENT_BYTE_1 = 0xef;
constexpr uint8_t UTF8_REPLACEMENT_BYTE_2 = 0xbf;
constexpr uint8_t UTF8_REPLACEMENT_BYTE_3 = 0xbd;

constexpr uint64_t UTF8_FAST_ASCII_MASK = 0x8080808080808080;
constexpr uint64_t UTF16_FAST_ASCII_MASK = 0xff80ff80ff80ff80;
constexpr uint16_t UTF16_NON_ASCII_MASK = 0xff80;
constexpr uint16_t UTF16_THREE_BYTE_MASK = 0xf800;
}  // namespace

TString tstr_new_invalid()
{
    TString tstr;
    tstr.flags = TSTRING_STORAGE_INVALID | TSTRING_ENCODING_UNKNOWN;
    tstr.byte_length = 0;
    tstr.data = nullptr;
    tstr.cb = nullptr;
    return tstr;
}

#if TH_ENABLE_STRING_SSO
namespace {
constexpr size_t UTF8_MAX_SHORT_CAPACITY = sizeof(void *) * 2 / sizeof(char);
constexpr size_t UTF8_MAX_SHORT_LENGTH = UTF8_MAX_SHORT_CAPACITY - 1;
constexpr size_t UTF16_MAX_SHORT_CAPACITY = sizeof(void *) * 2 / sizeof(uint16_t);
constexpr size_t UTF16_MAX_SHORT_LENGTH = UTF16_MAX_SHORT_CAPACITY - 1;
}  // namespace

char *tstr_initialize_short_utf8(TString *tstr_ptr)
{
    tstr_ptr->flags = TSTRING_STORAGE_SMALL | TSTRING_ENCODING_UTF8;
    return tstr_ptr->small_utf8;
}

uint16_t *tstr_initialize_short_utf16(TString *tstr_ptr)
{
    tstr_ptr->flags = TSTRING_STORAGE_SMALL | TSTRING_ENCODING_UTF16;
    return tstr_ptr->small_utf16;
}

TString tstr_new_short_utf8(char const *value TH_NONNULL, size_t len)
{
    TString tstr;
    char *buf = tstr_initialize_short_utf8(&tstr);
    char *end = std::copy_n(value, len, buf);
    *end = '\0';
    tstr_set_len_utf8(&tstr, end - buf);
    return tstr;
}

TString tstr_new_short_utf16(uint16_t const *value TH_NONNULL, size_t len)
{
    TString tstr;
    uint16_t *buf = tstr_initialize_short_utf16(&tstr);
    uint16_t *end = std::copy_n(value, len, buf);
    *end = u'\0';
    tstr_set_len_utf16(&tstr, end - buf);
    return tstr;
}
#endif

char *tstr_initialize_utf8(TString *tstr_ptr, size_t capacity)
{
#if TH_ENABLE_STRING_SSO
    if (capacity <= UTF8_MAX_SHORT_CAPACITY) {
        return tstr_initialize_short_utf8(tstr_ptr);
    }
#endif
    size_t bytes_required = sizeof(TStringControlBlock) + capacity * sizeof(char);
    TStringControlBlock *cb = reinterpret_cast<TStringControlBlock *>(malloc(bytes_required));
    if (!cb) {
        return nullptr;
    }

    tref_init(&cb->ref_count, 1);
    cb->drop = nullptr;
    cb->context = nullptr;

    char *buffer = reinterpret_cast<char *>(cb + 1);

    tstr_ptr->flags = TSTRING_STORAGE_INTERNAL | TSTRING_ENCODING_UTF8;
    tstr_set_buf_utf8(tstr_ptr, buffer);
    tstr_ptr->cb = cb;

    return buffer;
}

uint16_t *tstr_initialize_utf16(TString *tstr_ptr, size_t capacity)
{
#if TH_ENABLE_STRING_SSO
    if (capacity <= UTF16_MAX_SHORT_CAPACITY) {
        return tstr_initialize_short_utf16(tstr_ptr);
    }
#endif
    size_t bytes_required = sizeof(TStringControlBlock) + capacity * sizeof(uint16_t);
    TStringControlBlock *cb = reinterpret_cast<TStringControlBlock *>(malloc(bytes_required));
    if (!cb) {
        return nullptr;
    }

    tref_init(&cb->ref_count, 1);
    cb->drop = nullptr;
    cb->context = nullptr;

    uint16_t *buffer = reinterpret_cast<uint16_t *>(cb + 1);

    tstr_ptr->flags = TSTRING_STORAGE_INTERNAL | TSTRING_ENCODING_UTF16;
    tstr_set_buf_utf16(tstr_ptr, buffer);
    tstr_ptr->cb = cb;

    return buffer;
}

TString tstr_new_utf8(char const *value TH_NONNULL, size_t len)
{
#if TH_ENABLE_STRING_SSO
    if (len <= UTF8_MAX_SHORT_LENGTH) {
        return tstr_new_short_utf8(value, len);
    }
#endif
    TString tstr;
    char *buf = tstr_initialize_utf8(&tstr, len + 1);
    if (!buf) {
        return tstr_new_invalid();
    }

    char *end = std::copy_n(value, len, buf);
    *end = '\0';
    tstr_set_len_utf8(&tstr, end - buf);
    return tstr;
}

TString tstr_new_utf16(uint16_t const *value TH_NONNULL, size_t len)
{
#if TH_ENABLE_STRING_SSO
    if (len <= UTF16_MAX_SHORT_LENGTH) {
        return tstr_new_short_utf16(value, len);
    }
#endif
    TString tstr;
    uint16_t *buf = tstr_initialize_utf16(&tstr, len + 1);
    if (!buf) {
        return tstr_new_invalid();
    }

    uint16_t *end = std::copy_n(value, len, buf);
    *end = u'\0';
    tstr_set_len_utf16(&tstr, end - buf);
    return tstr;
}

TString tstr_new_borrowed_utf8(char const *buf TH_NONNULL, size_t len)
{
    TString tstr;
    tstr.flags = TSTRING_STORAGE_BORROWED | TSTRING_ENCODING_UTF8;
    tstr_set_buf_utf8(&tstr, buf);
    tstr_set_len_utf8(&tstr, len);
    tstr.cb = nullptr;
    return tstr;
}

TString tstr_new_borrowed_utf16(uint16_t const *buf TH_NONNULL, size_t len)
{
    TString tstr;
    tstr.flags = TSTRING_STORAGE_BORROWED | TSTRING_ENCODING_UTF16;
    tstr_set_buf_utf16(&tstr, buf);
    tstr_set_len_utf16(&tstr, len);
    tstr.cb = nullptr;
    return tstr;
}

TString tstr_new_from_external_utf8(char const *buf TH_NONNULL, size_t len, void *context, void (*drop)(void *))
{
#if TH_ENABLE_STRING_SSO
    if (len <= UTF8_MAX_SHORT_LENGTH) {
        TString result = tstr_new_short_utf8(buf, len);
        if (drop != nullptr) {
            drop(context);
        }
        return result;
    }
#endif
    TString tstr;
    size_t bytes_required = sizeof(TStringControlBlock);
    TStringControlBlock *cb = reinterpret_cast<TStringControlBlock *>(malloc(bytes_required));
    if (!cb) {
        if (drop != nullptr) {
            drop(context);
        }
        return tstr_new_invalid();
    }

    tref_init(&cb->ref_count, 1);
    cb->drop = drop;
    cb->context = context;

    tstr.flags = TSTRING_STORAGE_EXTERNAL | TSTRING_ENCODING_UTF8;
    tstr_set_buf_utf8(&tstr, buf);
    tstr_set_len_utf8(&tstr, len);
    tstr.cb = cb;
    return tstr;
}

TString tstr_new_from_external_utf16(uint16_t const *buf TH_NONNULL, size_t len, void *context, void (*drop)(void *))
{
#if TH_ENABLE_STRING_SSO
    if (len <= UTF16_MAX_SHORT_LENGTH) {
        TString result = tstr_new_short_utf16(buf, len);
        if (drop != nullptr) {
            drop(context);
        }
        return result;
    }
#endif
    TString tstr;
    size_t bytes_required = sizeof(TStringControlBlock);
    TStringControlBlock *cb = reinterpret_cast<TStringControlBlock *>(malloc(bytes_required));
    if (!cb) {
        if (drop != nullptr) {
            drop(context);
        }
        return tstr_new_invalid();
    }

    tref_init(&cb->ref_count, 1);
    cb->drop = drop;
    cb->context = context;

    tstr.flags = TSTRING_STORAGE_EXTERNAL | TSTRING_ENCODING_UTF16;
    tstr_set_buf_utf16(&tstr, buf);
    tstr_set_len_utf16(&tstr, len);
    tstr.cb = cb;
    return tstr;
}

TString tstr_new_from_static_utf8(char const *buf TH_NONNULL, size_t len)
{
    TString tstr;
    tstr.flags = TSTRING_STORAGE_STATIC | TSTRING_ENCODING_UTF8;
    tstr_set_buf_utf8(&tstr, buf);
    tstr_set_len_utf8(&tstr, len);
    tstr.cb = nullptr;
    return tstr;
}

TString tstr_new_from_static_utf16(uint16_t const *buf TH_NONNULL, size_t len)
{
    TString tstr;
    tstr.flags = TSTRING_STORAGE_STATIC | TSTRING_ENCODING_UTF16;
    tstr_set_buf_utf16(&tstr, buf);
    tstr_set_len_utf16(&tstr, len);
    tstr.cb = nullptr;
    return tstr;
}

TString tstr_dup(TString tstr)
{
    uint32_t mode = tstr_mode(tstr);
    if (mode == TSTRING_STORAGE_BORROWED) {
        if (tstr_encoding(tstr) == TSTRING_ENCODING_UTF8) {
            return tstr_new_utf8(tstr_buf_utf8(&tstr), tstr_len_utf8(tstr));
        }
        if (tstr_encoding(tstr) == TSTRING_ENCODING_UTF16) {
            return tstr_new_utf16(tstr_buf_utf16(&tstr), tstr_len_utf16(tstr));
        }
        return tstr_new_invalid();
    }
    if (mode == TSTRING_STORAGE_INTERNAL || mode == TSTRING_STORAGE_EXTERNAL) {
        tref_inc(&tstr.cb->ref_count);
    }
    return tstr;
}

void tstr_drop(TString tstr)
{
    uint32_t mode = tstr_mode(tstr);
    if (mode == TSTRING_STORAGE_INTERNAL || mode == TSTRING_STORAGE_EXTERNAL) {
        TStringControlBlock *cb = tstr.cb;
        if (tref_dec(&cb->ref_count)) {
            if (mode == TSTRING_STORAGE_EXTERNAL && cb->drop != nullptr) {
                cb->drop(cb->context);
            }
            free(cb);
        }
    }
}

namespace {
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
inline auto utf8_to_utf16(char const *buf, size_t len, Args &&...args)
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
                uint8_t const *final_pos = pos + UTF8_FAST_BLOCK_SIZE;
                while (pos < final_pos) {
                    sink.write(uint16_t(*pos++));
                }
                continue;
            }
        }

        uint8_t leading_byte = *pos;
        if (leading_byte < UTF8_NON_ASCII_MIN) {
            // ASCII
            pos += UTF8_ONE_BYTE_COUNT;
            sink.write(uint16_t(leading_byte));
        } else if ((leading_byte & UTF8_TWO_BYTE_PREFIX_MASK) == UTF8_TWO_BYTE_PREFIX) {
            // 2 字节 UTF-8
            if (pos + UTF8_CONTINUATION_BYTE_OFFSET >= end ||
                (*(pos + UTF8_CONTINUATION_BYTE_OFFSET) & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_PREFIX) {
                pos += UTF8_ONE_BYTE_COUNT;
                sink.write(UNICODE_REPLACEMENT_CHAR);
                continue;
            }
            uint32_t code_point = (leading_byte & UTF8_TWO_BYTE_PAYLOAD_MASK) << UTF8_SHIFT_1 |
                                  (*(pos + UTF8_CONTINUATION_BYTE_OFFSET) & UTF8_PAYLOAD_MASK);
            if (code_point < UTF8_TWO_BYTE_MIN || UTF8_TWO_BYTE_MAX < code_point) {
                pos += UTF8_ONE_BYTE_COUNT;
                sink.write(UNICODE_REPLACEMENT_CHAR);
                continue;
            }
            pos += UTF8_TWO_BYTE_COUNT;
            sink.write(uint16_t(code_point));
        } else if ((leading_byte & UTF8_THREE_BYTE_PREFIX_MASK) == UTF8_THREE_BYTE_PREFIX) {
            // 3 字节 UTF-8
            if (pos + UTF8_THREE_BYTE_LAST_OFFSET >= end ||
                (*(pos + UTF8_CONTINUATION_BYTE_OFFSET) & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_PREFIX ||
                (*(pos + UTF8_THREE_BYTE_LAST_OFFSET) & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_PREFIX) {
                pos += UTF8_ONE_BYTE_COUNT;
                sink.write(UNICODE_REPLACEMENT_CHAR);
                continue;
            }
            uint32_t code_point = (leading_byte & UTF8_THREE_BYTE_PAYLOAD_MASK) << UTF8_SHIFT_2 |
                                  (*(pos + UTF8_CONTINUATION_BYTE_OFFSET) & UTF8_PAYLOAD_MASK) << UTF8_SHIFT_1 |
                                  (*(pos + UTF8_THREE_BYTE_LAST_OFFSET) & UTF8_PAYLOAD_MASK);
            if (code_point < UTF8_THREE_BYTE_MIN || UTF8_THREE_BYTE_MAX < code_point ||
                (UTF16_SURROGATE_HIGH_START <= code_point && code_point <= UTF16_SURROGATE_LOW_END)) {
                pos += UTF8_ONE_BYTE_COUNT;
                sink.write(UNICODE_REPLACEMENT_CHAR);
                continue;
            }
            pos += UTF8_THREE_BYTE_COUNT;
            sink.write(uint16_t(code_point));
        } else if ((leading_byte & UTF8_FOUR_BYTE_PREFIX_MASK) == UTF8_FOUR_BYTE_PREFIX) {
            // 4 字节 UTF-8
            if (pos + UTF8_FOUR_BYTE_LAST_OFFSET >= end ||
                (*(pos + UTF8_CONTINUATION_BYTE_OFFSET) & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_PREFIX ||
                (*(pos + UTF8_THREE_BYTE_LAST_OFFSET) & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_PREFIX ||
                (*(pos + UTF8_FOUR_BYTE_LAST_OFFSET) & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_PREFIX) {
                pos += UTF8_ONE_BYTE_COUNT;
                sink.write(UNICODE_REPLACEMENT_CHAR);
                continue;
            }
            uint32_t code_point = (leading_byte & UTF8_FOUR_BYTE_PAYLOAD_MASK) << UTF8_SHIFT_3 |
                                  (*(pos + UTF8_CONTINUATION_BYTE_OFFSET) & UTF8_PAYLOAD_MASK) << UTF8_SHIFT_2 |
                                  (*(pos + UTF8_THREE_BYTE_LAST_OFFSET) & UTF8_PAYLOAD_MASK) << UTF8_SHIFT_1 |
                                  (*(pos + UTF8_FOUR_BYTE_LAST_OFFSET) & UTF8_PAYLOAD_MASK);
            if (code_point < UTF8_FOUR_BYTE_MIN || UTF8_FOUR_BYTE_MAX < code_point) {
                pos += UTF8_ONE_BYTE_COUNT;
                sink.write(UNICODE_REPLACEMENT_CHAR);
                continue;
            }
            pos += UTF8_FOUR_BYTE_COUNT;
            code_point -= UTF8_FOUR_BYTE_MIN;
            uint16_t high_surrogate = uint16_t(UTF16_SURROGATE_HIGH_START + (code_point >> UTF16_SURROGATE_SHIFT));
            uint16_t low_surrogate = uint16_t(UTF16_SURROGATE_LOW_START + (code_point & UTF16_SURROGATE_MASK));
            sink.write(high_surrogate);
            sink.write(low_surrogate);
        } else {
            pos += UTF8_ONE_BYTE_COUNT;
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
inline auto utf16_to_utf8(uint16_t const *buf, size_t len, Args &&...args)
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
                uint16_t const *final_pos = pos + UTF16_FAST_BLOCK_SIZE;
                while (pos < final_pos) {
                    sink.write(char(*pos++));
                }
                continue;
            }
        }

        uint16_t word = *pos;
        if ((word & UTF16_NON_ASCII_MASK) == 0) {
            pos += UTF16_ONE_UNIT_COUNT;
            sink.write(char(word));
        } else if ((word & UTF16_THREE_BYTE_MASK) == 0) {
            pos += UTF16_ONE_UNIT_COUNT;
            sink.write(char((word >> UTF8_SHIFT_1) | UTF8_TWO_BYTE_PREFIX));
            sink.write(char((word & UTF8_PAYLOAD_MASK) | UTF8_CONTINUATION_PREFIX));
        } else if ((word & UTF16_THREE_BYTE_MASK) != UTF16_SURROGATE_HIGH_START) {
            pos += UTF16_ONE_UNIT_COUNT;
            sink.write(char((word >> UTF8_SHIFT_2) | UTF8_THREE_BYTE_PREFIX));
            sink.write(char(((word >> UTF8_SHIFT_1) & UTF8_PAYLOAD_MASK) | UTF8_CONTINUATION_PREFIX));
            sink.write(char((word & UTF8_PAYLOAD_MASK) | UTF8_CONTINUATION_PREFIX));
        } else {
            // must be a surrogate pair
            uint16_t word_diff = uint16_t(word - UTF16_SURROGATE_HIGH_START);
            if (pos + UTF16_TRAIL_SURROGATE_OFFSET >= end || word_diff > UTF16_SURROGATE_MASK) {
                pos += UTF16_ONE_UNIT_COUNT;
                sink.write(char(UTF8_REPLACEMENT_BYTE_1));
                sink.write(char(UTF8_REPLACEMENT_BYTE_2));
                sink.write(char(UTF8_REPLACEMENT_BYTE_3));
                continue;
            }
            uint16_t next = *(pos + UTF16_TRAIL_SURROGATE_OFFSET);
            uint16_t next_diff = uint16_t(next - UTF16_SURROGATE_LOW_START);
            if (next_diff > UTF16_SURROGATE_MASK) {
                pos += UTF16_ONE_UNIT_COUNT;
                sink.write(char(UTF8_REPLACEMENT_BYTE_1));
                sink.write(char(UTF8_REPLACEMENT_BYTE_2));
                sink.write(char(UTF8_REPLACEMENT_BYTE_3));
                continue;
            }
            pos += UTF16_TWO_UNIT_COUNT;
            uint32_t value = (word_diff << UTF16_SURROGATE_SHIFT) + next_diff + UTF8_FOUR_BYTE_MIN;
            sink.write(char((value >> UTF8_SHIFT_3) | UTF8_FOUR_BYTE_PREFIX));
            sink.write(char(((value >> UTF8_SHIFT_2) & UTF8_PAYLOAD_MASK) | UTF8_CONTINUATION_PREFIX));
            sink.write(char(((value >> UTF8_SHIFT_1) & UTF8_PAYLOAD_MASK) | UTF8_CONTINUATION_PREFIX));
            sink.write(char((value & UTF8_PAYLOAD_MASK) | UTF8_CONTINUATION_PREFIX));
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
    if (tstr_encoding(tstr) == TSTRING_ENCODING_UTF16) {
        return tstr_dup(tstr);
    }
    char const *src = tstr_buf_utf8(&tstr);
    size_t len = tstr_len_utf8(tstr);
    if (tstr_encoding(tstr) == TSTRING_ENCODING_UTF8) {
        TString result;
        size_t needed = count_utf8_to_utf16(src, len);
        uint16_t *dst = tstr_initialize_utf16(&result, needed + 1);
        if (!dst) {
            return tstr_new_invalid();
        }

        uint16_t *end = write_utf8_to_utf16(src, len, dst);
        *end = u'\0';
        tstr_set_len_utf16(&result, end - dst);
        return result;
    }
    return tstr_new_invalid();
}

TString tstr_dup_as_utf8(TString tstr)
{
    if (tstr_encoding(tstr) == TSTRING_ENCODING_UTF8) {
        return tstr_dup(tstr);
    }
    uint16_t const *src = tstr_buf_utf16(&tstr);
    size_t len = tstr_len_utf16(tstr);
    if (tstr_encoding(tstr) == TSTRING_ENCODING_UTF16) {
        TString result;
        size_t needed = count_utf16_to_utf8(src, len);
        char *dst = tstr_initialize_utf8(&result, needed + 1);
        if (!dst) {
            return tstr_new_invalid();
        }

        char *end = write_utf16_to_utf8(src, len, dst);
        *end = '\0';
        tstr_set_len_utf8(&result, end - dst);
        return result;
    }
    return tstr_new_invalid();
}

TString tstr_concat_as_utf8(size_t count, TString const *tstr_list)
{
    TString result;
    size_t len = 0;
    for (size_t i = 0; i < count; ++i) {
        TString tstr = tstr_list[i];
        if (tstr_encoding(tstr) == TSTRING_ENCODING_UTF8) {
            len += tstr_len_utf8(tstr);
        } else if (tstr_encoding(tstr) == TSTRING_ENCODING_UTF16) {
            len += count_utf16_to_utf8(tstr_buf_utf16(&tstr), tstr_len_utf16(tstr));
        } else {
            return tstr_new_invalid();
        }
    }
    char *buf = tstr_initialize_utf8(&result, len + 1);
    if (!buf) {
        return tstr_new_invalid();
    }

    char *end = buf;
    for (size_t i = 0; i < count; ++i) {
        TString tstr = tstr_list[i];
        if (tstr_encoding(tstr) == TSTRING_ENCODING_UTF8) {
            end = std::copy_n(tstr_buf_utf8(&tstr), tstr_len_utf8(tstr), end);
        } else if (tstr_encoding(tstr) == TSTRING_ENCODING_UTF16) {
            end = write_utf16_to_utf8(tstr_buf_utf16(&tstr), tstr_len_utf16(tstr), end);
        }
    }
    *end = '\0';
    tstr_set_len_utf8(&result, end - buf);
    return result;
}

TString tstr_concat_as_utf16(size_t count, TString const *tstr_list)
{
    TString result;
    size_t len = 0;
    for (size_t i = 0; i < count; ++i) {
        TString tstr = tstr_list[i];
        if (tstr_encoding(tstr) == TSTRING_ENCODING_UTF16) {
            len += tstr_len_utf16(tstr);
        } else if (tstr_encoding(tstr) == TSTRING_ENCODING_UTF8) {
            len += count_utf8_to_utf16(tstr_buf_utf8(&tstr), tstr_len_utf8(tstr));
        } else {
            return tstr_new_invalid();
        }
    }
    uint16_t *buf = tstr_initialize_utf16(&result, len + 1);
    if (!buf) {
        return tstr_new_invalid();
    }

    uint16_t *end = buf;
    for (size_t i = 0; i < count; ++i) {
        TString tstr = tstr_list[i];
        if (tstr_encoding(tstr) == TSTRING_ENCODING_UTF16) {
            end = std::copy_n(tstr_buf_utf16(&tstr), tstr_len_utf16(tstr), end);
        } else if (tstr_encoding(tstr) == TSTRING_ENCODING_UTF8) {
            end = write_utf8_to_utf16(tstr_buf_utf8(&tstr), tstr_len_utf8(tstr), end);
        }
    }
    *end = u'\0';
    tstr_set_len_utf16(&result, end - buf);
    return result;
}

TString tstr_substr_utf8(TString tstr, size_t pos, size_t len)
{
    if (tstr_encoding(tstr) != TSTRING_ENCODING_UTF8) {
        return tstr_new_invalid();
    }

    size_t const orig_len = tstr_len_utf8(tstr);
    if (pos > orig_len) {
        pos = orig_len;
    }
    size_t const remaining = orig_len - pos;
    if (len > remaining) {
        len = remaining;
    }

#if TH_ENABLE_STRING_SSO
    uint32_t mode = tstr_mode(tstr);
    // An SSO buffer is embedded in the by-value input, so it must be copied.
    if (mode == TSTRING_STORAGE_SMALL) {
        return tstr_new_short_utf8(tstr_buf_utf8(&tstr) + pos, len);
    }
#endif

#if TH_ENABLE_RETAINABLE_SUBSTR

#if TH_ENABLE_STRING_SSO
    // Sharing a short ref-counted slice would bypass SSO, so we do it explicitly here.
    if ((len <= UTF8_MAX_SHORT_LENGTH && (mode == TSTRING_STORAGE_INTERNAL || mode == TSTRING_STORAGE_EXTERNAL))) {
        return tstr_new_short_utf8(tstr_buf_utf8(&tstr) + pos, len);
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
        return tstr_new_invalid();
    }

    size_t const orig_len = tstr_len_utf16(tstr);
    if (pos > orig_len) {
        pos = orig_len;
    }
    size_t const remaining = orig_len - pos;
    if (len > remaining) {
        len = remaining;
    }

#if TH_ENABLE_STRING_SSO
    uint32_t mode = tstr_mode(tstr);
    // An SSO buffer is embedded in the by-value input, so it must be copied.
    if (mode == TSTRING_STORAGE_SMALL) {
        return tstr_new_short_utf16(tstr_buf_utf16(&tstr) + pos, len);
    }
#endif

#if TH_ENABLE_RETAINABLE_SUBSTR

#if TH_ENABLE_STRING_SSO
    // Sharing a short ref-counted slice would bypass SSO, so we do it explicitly here.
    if ((len <= UTF16_MAX_SHORT_LENGTH && (mode == TSTRING_STORAGE_INTERNAL || mode == TSTRING_STORAGE_EXTERNAL))) {
        return tstr_new_short_utf16(tstr_buf_utf16(&tstr) + pos, len);
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
