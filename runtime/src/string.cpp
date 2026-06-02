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

namespace {

constexpr size_t UTF8_FAST_BLOCK_SIZE = 16;
constexpr size_t UTF8_FAST_WORD_SIZE = 8;
constexpr size_t UTF16_FAST_BLOCK_SIZE = 4;

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
    struct TString tstr;
    tstr.flags = 0;
    tstr.length = 0;
    tstr.pstrinfo = nullptr;
    tstr.ptr = nullptr;
    return tstr;
}

char *tstr_initialize(struct TString *tstr_ptr, uint32_t capacity)
{
    size_t bytes_required = sizeof(struct TStringInfo) + capacity;
    struct TStringInfo *sh = reinterpret_cast<struct TStringInfo *>(malloc(bytes_required));
    if (!sh) {
        return nullptr;
    }

    tref_init(&sh->count, 1);
    sh->drop = nullptr;
    sh->external_obj = nullptr;

    char *buffer = reinterpret_cast<char *>(sh + 1);

    tstr_ptr->flags = TSTRING_UTF8;
    tstr_ptr->pstrinfo = sh;
    tstr_ptr->ptr = buffer;

    return buffer;
}

uint16_t *tstr_initialize_utf16(struct TString *tstr_ptr, uint32_t capacity)
{
    size_t bytes_required = sizeof(struct TStringInfo) + capacity * sizeof(uint16_t);
    struct TStringInfo *sh = reinterpret_cast<struct TStringInfo *>(malloc(bytes_required));
    if (!sh) {
        return nullptr;
    }

    tref_init(&sh->count, 1);
    sh->drop = nullptr;
    sh->external_obj = nullptr;

    char *buffer = reinterpret_cast<char *>(sh + 1);

    tstr_ptr->flags = TSTRING_UTF16;
    tstr_ptr->pstrinfo = sh;
    tstr_ptr->ptr = buffer;

    return reinterpret_cast<uint16_t *>(buffer);
}

struct TString tstr_new(char const *value TH_NONNULL, size_t len)
{
    struct TString tstr;
    char *buf = tstr_initialize(&tstr, len + 1);
    buf = std::copy(value, value + len, buf);
    *buf = '\0';
    tstr_set_len(&tstr, len);
    return tstr;
}

struct TString tstr_new_utf16(uint16_t const *value TH_NONNULL, size_t len)
{
    struct TString tstr;
    uint16_t *buf = tstr_initialize_utf16(&tstr, len + 1);
    buf = std::copy(value, value + len, buf);
    *buf = u'\0';
    tstr_set_len_utf16(&tstr, len);
    return tstr;
}

struct TString tstr_new_ref(char const *buf TH_NONNULL, size_t len)
{
    struct TString tstr;
    tstr.flags = TSTRING_REF | TSTRING_UTF8;
    tstr_set_len(&tstr, len);
    tstr.pstrinfo = nullptr;
    tstr.ptr = buf;
    return tstr;
}

struct TString tstr_new_ref_utf16(uint16_t const *buf TH_NONNULL, size_t len)
{
    struct TString tstr;
    tstr.flags = TSTRING_REF | TSTRING_UTF16;
    tstr_set_len_utf16(&tstr, len);
    tstr.pstrinfo = nullptr;
    tstr.ptr = reinterpret_cast<char const *>(buf);
    return tstr;
}

struct TString tstr_new_from_external(char const *buf TH_NONNULL, size_t len, void *external_obj, void (*drop)(void *))
{
    struct TString tstr;
    struct TStringInfo *info = reinterpret_cast<struct TStringInfo *>(malloc(sizeof(struct TStringInfo)));
    if (!info) {
        return tstr_new_invalid();
    }
    tref_init(&info->count, 1);
    info->drop = drop;
    info->external_obj = external_obj;

    tstr.flags = TSTRING_UTF8 | TSTRING_EXT;
    tstr_set_len(&tstr, len);
    tstr.pstrinfo = info;
    tstr.ptr = buf;

    return tstr;
}

struct TString tstr_new_from_external_utf16(uint16_t const *buf TH_NONNULL, size_t len, void *external_obj,
                                            void (*drop)(void *))
{
    struct TString tstr;
    struct TStringInfo *info = reinterpret_cast<struct TStringInfo *>(malloc(sizeof(struct TStringInfo)));
    if (!info) {
        return tstr_new_invalid();
    }
    tref_init(&info->count, 1);
    info->drop = drop;
    info->external_obj = external_obj;

    tstr.flags = TSTRING_UTF16 | TSTRING_EXT;
    tstr_set_len_utf16(&tstr, len);
    tstr.pstrinfo = info;
    tstr.ptr = reinterpret_cast<char const *>(buf);

    return tstr;
}

struct TString tstr_dup(struct TString orig)
{
    // ref 需创建堆内存
    // sh、external 不需要创建新的堆内存
    if ((orig.flags & TSTRING_REF) == 0) {
        tref_inc(&orig.pstrinfo->count);
        return orig;
    }

    if (tstr_encoding(orig) == TSTRING_UTF8) {
        return tstr_new(tstr_buf(orig), tstr_len(orig));
    } else if (tstr_encoding(orig) == TSTRING_UTF16) {
        return tstr_new_utf16(tstr_buf_utf16(orig), tstr_len_utf16(orig));
    } else {
        return tstr_new_invalid();
    }
}

void tstr_drop(struct TString tstr)
{
    if (tstr.flags & TSTRING_REF) {
        return;
    }
    struct TStringInfo *sh = tstr.pstrinfo;
    if (!sh) {
        return;
    }
    if (tref_dec(&sh->count)) {
        if ((tstr.flags & TSTRING_EXT) && sh->drop) {
            sh->drop(sh->external_obj);
        }
        free(sh);
    }
}

inline size_t utf8_to_utf16_required(char const *src, size_t len)
{
    uint8_t const *data = reinterpret_cast<uint8_t const *>(src);
    size_t pos = 0;
    size_t units = 0;

    while (pos < len) {
        if (pos + UTF8_FAST_BLOCK_SIZE <= len) {
            uint64_t v1;
            uint64_t v2;
            std::copy(data + pos, data + pos + UTF8_FAST_WORD_SIZE, reinterpret_cast<uint8_t *>(&v1));
            std::copy(data + pos + UTF8_FAST_WORD_SIZE, data + pos + UTF8_FAST_BLOCK_SIZE,
                      reinterpret_cast<uint8_t *>(&v2));
            uint64_t v = v1 | v2;
            if ((v & UTF8_FAST_ASCII_MASK) == 0) {
                units += UTF8_FAST_BLOCK_SIZE;
                pos += UTF8_FAST_BLOCK_SIZE;
                continue;
            }
        }

        uint8_t leading_byte = data[pos];
        if (leading_byte < UTF8_NON_ASCII_MIN) {
            // ASCII
            units += UTF16_ONE_UNIT_COUNT;
            pos++;
        } else if ((leading_byte & UTF8_TWO_BYTE_PREFIX_MASK) == UTF8_TWO_BYTE_PREFIX) {
            // 2 字节 UTF-8
            if (pos + UTF8_CONTINUATION_BYTE_OFFSET >= len ||
                (data[pos + UTF8_CONTINUATION_BYTE_OFFSET] & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_PREFIX) {
                units += UTF16_ONE_UNIT_COUNT;
                pos++;
                continue;
            }
            units += UTF16_ONE_UNIT_COUNT;
            pos += UTF8_TWO_BYTE_COUNT;
        } else if ((leading_byte & UTF8_THREE_BYTE_PREFIX_MASK) == UTF8_THREE_BYTE_PREFIX) {
            // 3 字节 UTF-8
            if (pos + UTF8_THREE_BYTE_LAST_OFFSET >= len ||
                (data[pos + UTF8_CONTINUATION_BYTE_OFFSET] & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_PREFIX ||
                (data[pos + UTF8_THREE_BYTE_LAST_OFFSET] & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_PREFIX) {
                units += UTF16_ONE_UNIT_COUNT;
                pos++;
                continue;
            }
            units += UTF16_ONE_UNIT_COUNT;
            pos += UTF8_THREE_BYTE_COUNT;
        } else if ((leading_byte & UTF8_FOUR_BYTE_PREFIX_MASK) == UTF8_FOUR_BYTE_PREFIX) {
            // 4 字节 UTF-8
            if (pos + UTF8_FOUR_BYTE_LAST_OFFSET >= len ||
                (data[pos + UTF8_CONTINUATION_BYTE_OFFSET] & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_PREFIX ||
                (data[pos + UTF8_THREE_BYTE_LAST_OFFSET] & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_PREFIX ||
                (data[pos + UTF8_FOUR_BYTE_LAST_OFFSET] & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_PREFIX) {
                units += UTF16_ONE_UNIT_COUNT;
                pos++;
                continue;
            }
            units += UTF16_TWO_UNIT_COUNT;
            pos += UTF8_FOUR_BYTE_COUNT;
        } else {
            units += UTF16_ONE_UNIT_COUNT;
            pos++;
        }
    }
    return units;
}

inline size_t utf8_to_utf16(char const *input, size_t len, uint16_t *output)
{
    uint8_t const *data = reinterpret_cast<uint8_t const *>(input);
    size_t pos = 0;
    uint16_t *start {output};

    while (pos < len) {
        if (pos + UTF8_FAST_BLOCK_SIZE <= len) {
            uint64_t v1;
            uint64_t v2;
            std::copy(data + pos, data + pos + UTF8_FAST_WORD_SIZE, reinterpret_cast<uint8_t *>(&v1));
            std::copy(data + pos + UTF8_FAST_WORD_SIZE, data + pos + UTF8_FAST_BLOCK_SIZE,
                      reinterpret_cast<uint8_t *>(&v2));
            uint64_t v {v1 | v2};
            if ((v & UTF8_FAST_ASCII_MASK) == 0) {
                size_t final_pos = pos + UTF8_FAST_BLOCK_SIZE;
                while (pos < final_pos) {
                    *output++ = uint16_t(input[pos]);
                    pos++;
                }
                continue;
            }
        }

        uint8_t leading_byte = data[pos];
        if (leading_byte < UTF8_NON_ASCII_MIN) {
            // ASCII
            *output++ = uint16_t(leading_byte);
            pos++;
        } else if ((leading_byte & UTF8_TWO_BYTE_PREFIX_MASK) == UTF8_TWO_BYTE_PREFIX) {
            // 2 字节 UTF-8
            if (pos + UTF8_CONTINUATION_BYTE_OFFSET >= len ||
                (data[pos + UTF8_CONTINUATION_BYTE_OFFSET] & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_PREFIX) {
                *output++ = UNICODE_REPLACEMENT_CHAR;
                pos++;
                continue;
            }
            uint32_t code_point = (leading_byte & UTF8_TWO_BYTE_PAYLOAD_MASK) << UTF8_SHIFT_1 |
                                  (data[pos + UTF8_CONTINUATION_BYTE_OFFSET] & UTF8_PAYLOAD_MASK);
            if (code_point < UTF8_TWO_BYTE_MIN || UTF8_TWO_BYTE_MAX < code_point) {
                return 0;
            }
            *output++ = uint16_t(code_point);
            pos += UTF8_TWO_BYTE_COUNT;
        } else if ((leading_byte & UTF8_THREE_BYTE_PREFIX_MASK) == UTF8_THREE_BYTE_PREFIX) {
            // 3 字节 UTF-8
            if (pos + UTF8_THREE_BYTE_LAST_OFFSET >= len ||
                (data[pos + UTF8_CONTINUATION_BYTE_OFFSET] & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_PREFIX ||
                (data[pos + UTF8_THREE_BYTE_LAST_OFFSET] & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_PREFIX) {
                *output++ = UNICODE_REPLACEMENT_CHAR;
                pos++;
                continue;
            }
            uint32_t code_point = (leading_byte & UTF8_THREE_BYTE_PAYLOAD_MASK) << UTF8_SHIFT_2 |
                                  (data[pos + UTF8_CONTINUATION_BYTE_OFFSET] & UTF8_PAYLOAD_MASK) << UTF8_SHIFT_1 |
                                  (data[pos + UTF8_THREE_BYTE_LAST_OFFSET] & UTF8_PAYLOAD_MASK);
            if (code_point < UTF8_THREE_BYTE_MIN || UTF8_THREE_BYTE_MAX < code_point ||
                (UTF16_SURROGATE_HIGH_START <= code_point && code_point <= UTF16_SURROGATE_LOW_END)) {
                return 0;
            }
            *output++ = uint16_t(code_point);
            pos += UTF8_THREE_BYTE_COUNT;
        } else if ((leading_byte & UTF8_FOUR_BYTE_PREFIX_MASK) == UTF8_FOUR_BYTE_PREFIX) {
            // 4 字节 UTF-8
            if (pos + UTF8_FOUR_BYTE_LAST_OFFSET >= len ||
                (data[pos + UTF8_CONTINUATION_BYTE_OFFSET] & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_PREFIX ||
                (data[pos + UTF8_THREE_BYTE_LAST_OFFSET] & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_PREFIX ||
                (data[pos + UTF8_FOUR_BYTE_LAST_OFFSET] & UTF8_CONTINUATION_MASK) != UTF8_CONTINUATION_PREFIX) {
                *output++ = UNICODE_REPLACEMENT_CHAR;
                pos++;
                continue;
            }
            uint32_t code_point = (leading_byte & UTF8_FOUR_BYTE_PAYLOAD_MASK) << UTF8_SHIFT_3 |
                                  (data[pos + UTF8_CONTINUATION_BYTE_OFFSET] & UTF8_PAYLOAD_MASK) << UTF8_SHIFT_2 |
                                  (data[pos + UTF8_THREE_BYTE_LAST_OFFSET] & UTF8_PAYLOAD_MASK) << UTF8_SHIFT_1 |
                                  (data[pos + UTF8_FOUR_BYTE_LAST_OFFSET] & UTF8_PAYLOAD_MASK);
            if (code_point < UTF8_FOUR_BYTE_MIN || UTF8_FOUR_BYTE_MAX < code_point) {
                return 0;
            }
            code_point -= UTF8_FOUR_BYTE_MIN;
            uint16_t high_surrogate = uint16_t(UTF16_SURROGATE_HIGH_START + (code_point >> UTF16_SURROGATE_SHIFT));
            uint16_t low_surrogate = uint16_t(UTF16_SURROGATE_LOW_START + (code_point & UTF16_SURROGATE_MASK));
            *output++ = high_surrogate;
            *output++ = low_surrogate;
            pos += UTF8_FOUR_BYTE_COUNT;
        } else {
            return 0;
        }
    }
    return output - start;
}

inline size_t utf16_to_utf8_required(uint16_t const *src, size_t len)
{
    uint16_t const *data = src;
    size_t pos = 0;
    size_t units = 0;
    while (pos < len) {
        if (pos + UTF16_FAST_BLOCK_SIZE <= len) {
            uint64_t v;
            std::copy(data + pos, data + pos + UTF16_FAST_BLOCK_SIZE, reinterpret_cast<uint8_t *>(&v));
            if ((v & UTF16_FAST_ASCII_MASK) == 0) {
                units += UTF16_FAST_BLOCK_SIZE;
                pos += UTF16_FAST_BLOCK_SIZE;
                continue;
            }
        }
        uint16_t word = data[pos];
        if ((word & UTF16_NON_ASCII_MASK) == 0) {
            units += UTF8_ONE_BYTE_COUNT;
            pos++;
        } else if ((word & UTF16_THREE_BYTE_MASK) == 0) {
            units += UTF8_TWO_BYTE_COUNT;
            pos++;
        } else if ((word & UTF16_THREE_BYTE_MASK) != UTF16_SURROGATE_HIGH_START) {
            units += UTF8_THREE_BYTE_COUNT;
            pos++;
        } else {
            // must be a surrogate pair
            uint16_t diff = uint16_t(word - UTF16_SURROGATE_HIGH_START);
            if (pos + UTF16_TRAIL_SURROGATE_OFFSET >= len || diff > UTF16_SURROGATE_MASK) {
                units += UTF8_THREE_BYTE_COUNT;
                pos++;
                continue;
            }
            if (uint16_t(data[pos + UTF16_TRAIL_SURROGATE_OFFSET] - UTF16_SURROGATE_LOW_START) > UTF16_SURROGATE_MASK) {
                units += UTF8_THREE_BYTE_COUNT;
                pos++;
                continue;
            }
            units += UTF8_FOUR_BYTE_COUNT;
            pos += UTF16_TWO_UNIT_COUNT;
        }
    }
    return units;
}

inline size_t utf16_to_utf8(uint16_t const *input, size_t len, char *output)
{
    uint16_t const *data = input;
    size_t pos = 0;
    char *start {output};
    while (pos < len) {
        if (pos + UTF16_FAST_BLOCK_SIZE <= len) {
            uint64_t v;
            std::copy(data + pos, data + pos + UTF16_FAST_BLOCK_SIZE, reinterpret_cast<uint8_t *>(&v));
            if ((v & UTF16_FAST_ASCII_MASK) == 0) {
                size_t final_pos = pos + UTF16_FAST_BLOCK_SIZE;
                while (pos < final_pos) {
                    *output++ = char(input[pos]);
                    pos++;
                }
                continue;
            }
        }
        uint16_t word = data[pos];
        if ((word & UTF16_NON_ASCII_MASK) == 0) {
            *output++ = char(word);
            pos++;
        } else if ((word & UTF16_THREE_BYTE_MASK) == 0) {
            *output++ = char((word >> UTF8_SHIFT_1) | UTF8_TWO_BYTE_PREFIX);
            *output++ = char((word & UTF8_PAYLOAD_MASK) | UTF8_CONTINUATION_PREFIX);
            pos++;
        } else if ((word & UTF16_THREE_BYTE_MASK) != UTF16_SURROGATE_HIGH_START) {
            *output++ = char((word >> UTF8_SHIFT_2) | UTF8_THREE_BYTE_PREFIX);
            *output++ = char(((word >> UTF8_SHIFT_1) & UTF8_PAYLOAD_MASK) | UTF8_CONTINUATION_PREFIX);
            *output++ = char((word & UTF8_PAYLOAD_MASK) | UTF8_CONTINUATION_PREFIX);
            pos++;
        } else {
            // must be a surrogate pair
            uint16_t diff = uint16_t(word - UTF16_SURROGATE_HIGH_START);
            if (pos + UTF16_TRAIL_SURROGATE_OFFSET >= len || diff > UTF16_SURROGATE_MASK) {
                *output++ = char(UTF8_REPLACEMENT_BYTE_1);
                *output++ = char(UTF8_REPLACEMENT_BYTE_2);
                *output++ = char(UTF8_REPLACEMENT_BYTE_3);
                pos++;
                continue;
            }
            uint16_t next_word = data[pos + UTF16_TRAIL_SURROGATE_OFFSET];
            uint16_t diff2 = uint16_t(next_word - UTF16_SURROGATE_LOW_START);
            if (diff2 > UTF16_SURROGATE_MASK) {
                *output++ = char(UTF8_REPLACEMENT_BYTE_1);
                *output++ = char(UTF8_REPLACEMENT_BYTE_2);
                *output++ = char(UTF8_REPLACEMENT_BYTE_3);
                pos++;
                continue;
            }

            uint32_t value = (diff << UTF16_SURROGATE_SHIFT) + diff2 + UTF8_FOUR_BYTE_MIN;
            *output++ = char((value >> UTF8_SHIFT_3) | UTF8_FOUR_BYTE_PREFIX);
            *output++ = char(((value >> UTF8_SHIFT_2) & UTF8_PAYLOAD_MASK) | UTF8_CONTINUATION_PREFIX);
            *output++ = char(((value >> UTF8_SHIFT_1) & UTF8_PAYLOAD_MASK) | UTF8_CONTINUATION_PREFIX);
            *output++ = char((value & UTF8_PAYLOAD_MASK) | UTF8_CONTINUATION_PREFIX);
            pos += UTF16_TWO_UNIT_COUNT;
        }
    }
    return output - start;
}

struct TString tstr_utf8_to_utf16(struct TString utf8_str)
{
    if (tstr_encoding(utf8_str) == TSTRING_UTF16) return tstr_dup(utf8_str);

    char const *src = tstr_buf(utf8_str);
    size_t len = tstr_len(utf8_str);

    size_t needed = utf8_to_utf16_required(src, len);

    struct TString result;
    uint16_t *dst = tstr_initialize_utf16(&result, (needed + 1));

    if (!dst) {
        return tstr_new_invalid();
    }

    size_t used_len = utf8_to_utf16(src, len, dst);
    dst[used_len] = u'\0';
    result.flags = TSTRING_UTF16;
    tstr_set_len_utf16(&result, used_len);
    return result;
}

struct TString tstr_utf16_to_utf8(struct TString utf16_str)
{
    if (tstr_encoding(utf16_str) == TSTRING_UTF8) return tstr_dup(utf16_str);

    uint16_t const *src = tstr_buf_utf16(utf16_str);
    size_t len = tstr_len_utf16(utf16_str);

    size_t needed = utf16_to_utf8_required(src, len);

    struct TString result;
    char *dst = tstr_initialize(&result, (needed + 1));

    if (!dst) {
        return tstr_new_invalid();
    }

    size_t used_len = utf16_to_utf8(src, len, dst);
    dst[used_len] = '\0';
    result.flags = TSTRING_UTF8;
    tstr_set_len(&result, used_len);
    return result;
}

struct TString tstr_concat(size_t count, struct TString const *tstr_list)
{
    size_t len = 0;
    for (size_t i = 0; i < count; ++i) {
        len += tstr_len(tstr_list[i]);
    }
    struct TString tstr;
    char *buf = tstr_initialize(&tstr, len + 1);
    for (size_t i = 0; i < count; ++i) {
        buf = std::copy(tstr_buf(tstr_list[i]), tstr_buf(tstr_list[i]) + tstr_len(tstr_list[i]), buf);
    }
    *buf = '\0';
    tstr_set_len(&tstr, len);
    return tstr;
}

struct TString tstr_concat_utf16(size_t count, struct TString const *tstr_list)
{
    size_t len = 0;
    for (size_t i = 0; i < count; ++i) {
        len += tstr_len_utf16(tstr_list[i]);
    }
    struct TString tstr;
    uint16_t *buf = tstr_initialize_utf16(&tstr, len + 1);
    for (size_t i = 0; i < count; ++i) {
        buf = std::copy(tstr_buf_utf16(tstr_list[i]), tstr_buf_utf16(tstr_list[i]) + tstr_len_utf16(tstr_list[i]), buf);
    }
    *buf = u'\0';
    tstr_set_len_utf16(&tstr, len);
    return tstr;
}

struct TString tstr_substr(struct TString tstr, size_t pos, size_t len)
{
    size_t orig_len = tstr_len(tstr);
    if (pos > orig_len) {
        len = 0;
    } else if (pos + len > orig_len) {
        len = orig_len - pos;
    }
    return tstr_new_ref(tstr_buf(tstr) + pos, len);
}

struct TString tstr_substr_utf16(struct TString tstr, size_t pos, size_t len)
{
    size_t orig_len = tstr_len_utf16(tstr);
    if (pos > orig_len) {
        len = 0;
    } else if (pos + len > orig_len) {
        len = orig_len - pos;
    }
    return tstr_new_ref_utf16(tstr_buf_utf16(tstr) + pos, len);
}
