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

#ifndef TAIHE_STRING_ABI_H
#define TAIHE_STRING_ABI_H

#include <taihe/common.h>

#include <stddef.h>
#include <stdint.h>

/////////////////////////////////////////
// Private ABI: Don't use in your code //
/////////////////////////////////////////

enum TStringFlags {
    TSTRING_MODE_MASK = 0xFFFF,
    TSTRING_ENCODING_MASK = 0xFFFF0000,
    TSTRING_REF = 1u,
    TSTRING_EXT = 1u << 1,
    TSTRING_UTF8 = 1u << 16,
    TSTRING_UTF16 = 1u << 17,
};

struct TStringInfo {
    TRefCount count;
    void (*drop)(void *);
    void *external_obj;
};

struct TString {
    uint32_t flags;
    uint32_t length;
    struct TStringInfo *pstrinfo;
    char const *ptr;
};

//////////////////
// Public C API //
//////////////////

// Returns the buffer of the TString.
TH_INLINE const char *tstr_buf(struct TString tstr)
{
    return tstr.ptr;
}

TH_INLINE const uint16_t *tstr_buf_utf16(struct TString tstr)
{
    return reinterpret_cast<uint16_t const *>(tstr.ptr);
}

// Returns the length of the TString.
TH_INLINE size_t tstr_len(struct TString tstr)
{
    return tstr.length;
}

TH_INLINE size_t tstr_len_utf16(struct TString tstr)
{
    return tstr.length / sizeof(uint16_t);
}

TH_INLINE uint32_t tstr_empty(struct TString tstr)
{
    return tstr.length == 0;
}

TH_INLINE uint32_t tstr_encoding(struct TString tstr)
{
    return tstr.flags & TSTRING_ENCODING_MASK;
}

TH_INLINE void tstr_set_len(struct TString *tstr_ptr, size_t len)
{
    tstr_ptr->length = len;
}

TH_INLINE void tstr_set_len_utf16(struct TString *tstr_ptr, size_t len)
{
    tstr_ptr->length = len * sizeof(uint16_t);
}

// Allocates memory and initializes a UTF8 encoding TString with a given
// capacity.
//
// # Arguments
// - `tstr_ptr`: Pointer to an uninitialized TString structure.
// - `capacity`: The desired capacity of the string buffer.
//
// # Returns
// - Pointer to the allocated buffer.
//
// # Notes
// - The caller is responsible for setting the string length.
// - Reference count is set to 1 after called.
TH_EXPORT char *tstr_initialize(struct TString *tstr_ptr, uint32_t capacity);

// Allocates memory and initializes a UTF16 encoding TString with a given
// capacity.
//
// # Arguments
// - `tstr_ptr`: Pointer to an uninitialized TString structure.
// - `capacity`: The desired capacity of the string buffer.
//
// # Returns
// - Pointer to the allocated buffer.
//
// # Notes
// - The caller is responsible for setting the string length.
// - Reference count is set to 1 after called.
TH_EXPORT uint16_t *tstr_initialize_utf16(struct TString *tstr_ptr, uint32_t capacity);

// Creates a new heap-allocated TString by copying an existing UTF8 string.
//
// # Arguments
// - `buf`: A null-terminated string (must not be null).
// - `len`: The length of the string.
//
// # Returns
// - A new TString containing a copy of `buf`.
//
// # Notes
// - The returned TString must be freed using `tstr_drop`.
TH_EXPORT struct TString tstr_new(char const *buf TH_NONNULL, size_t len);

// Creates a TString from an existing UTF8 string.
//
// # Arguments
// - `buf`: a null-terminated string. Null pointer is invalid.
// - `len`: the length of the string.
// - `tstr`: pointer to an uninitialized TString. Do not pass an
//    already-initialized TString here.
//
// # Returns
// - `tstr`, if the string is created successfully. The caller must ensure the
//    string buffer and the returned TString remain unchanged during the whole
//    lifetime of the TString.
// - `NULL`, if the string is not null-terminated, or the length is too large.
//    In this case, the original `tstr` is still uninitialized and should not be
//    used.
TH_EXPORT struct TString tstr_new_ref(char const *buf TH_NONNULL, size_t len);

// Creates a new heap-allocated TString by copying an existing UTF16 string.
//
// # Arguments
// - `buf`: A null-terminated string (must not be null).
// - `len`: The length of the string.
//
// # Returns
// - A new TString containing a copy of `buf`.
//
// # Notes
// - The returned TString must be freed using `tstr_drop`.
TH_EXPORT struct TString tstr_new_utf16(uint16_t const *buf TH_NONNULL, size_t len);

// Creates a TString from an existing UTF16 string.
//
// # Arguments
// - `buf`: a null-terminated string. Null pointer is invalid.
// - `len`: the length of the string.
// - `tstr`: pointer to an uninitialized TString. Do not pass an
//    already-initialized TString here.
//
// # Returns
// - `tstr`, if the string is created successfully. The caller must ensure the
//    string buffer and the returned TString remain unchanged during the whole
//    lifetime of the TString.
// - `NULL`, if the string is not null-terminated, or the length is too large.
//    In this case, the original `tstr` is still uninitialized and should not be
//    used.
TH_EXPORT struct TString tstr_new_ref_utf16(uint16_t const *buf TH_NONNULL, size_t len);

// Frees a TString, releasing allocated memory if applicable.
//
// # Arguments
// - `tstr`: The TString to be freed.
//
// # Notes
// - The TString should not be accessed after calling this function.
TH_EXPORT void tstr_drop(struct TString tstr);

// Creates a duplicate of a TString.
//
// # Arguments
// - `tstr`: The TString to be copied.
//
// # Returns
// - A new TString that is either a reference or a deep copy.
//
// # Notes
// - If `tstr` is heap-allocated, its reference count is incremented.
// - If `tstr` is a reference, a new heap-allocated copy is created.
// - Use `tstr_drop` to free the duplicate when done.
TH_EXPORT struct TString tstr_dup(struct TString tstr);

// Concatenates two UTF-8 TString objects.
//
// # Parameters
// - `count`: The number of strings to concatenate.
// - `tstr_list`: An array of TString objects to concatenate.
//
// # Returns
// - A new TString object containing the concatenated result.
//
// # Notes
// - The returned TString must be freed using `tstr_drop`.
TH_EXPORT struct TString tstr_concat(size_t count, struct TString const *tstr_list);

// Extracts a substring from a UTF-8 TString object.
//
// # Parameters
// - `tstr`: The source TString object to extract the substring from.
// - `pos`: The starting position of the substring within the source TString
//   object.
// - `len`: The length of the substring to extract.
//
// # Returns
// - A TString reference of the extracted substring.
//
// # Notes
// - The returned TString is just a view of the original string and does not own
//   the memory, so it should not be freed.
TH_EXPORT struct TString tstr_substr(struct TString tstr, size_t pos, size_t len);

// Converts a UTF8-encoded TString object into a UTF16-encoded TString.
//
// # Parameters
// - `utf8_str`: The source TString encoded in UTF8.
//
// # Returns
// - A new TString encoded in UTF16.
//   The returned TString owns its memory and must be freed with `tstr_drop`.
//
// # Notes
// - Invalid UTF8 sequences are handled according to the internal conversion
//   policy (typically replacing invalid sequences with U+FFFD).
// - Serious errors return an empty string U'\0'.
// - The returned TString is heap-allocated and independent of the input.
TH_EXPORT struct TString tstr_utf8_to_utf16(struct TString utf8_str);

// Converts a UTF16-encoded TString object into a UTF8-encoded TString.
//
// # Parameters
// - `utf16_str`: The source TString encoded in UTF16.
//
// # Returns
// - A new TString encoded in UTF8.
//   The returned TString owns its memory and must be freed with `tstr_drop`.
//
// # Notes
// - Invalid surrogate pairs or malformed UTF16 sequences are handled according
//   to the internal conversion policy (typically replacing invalid sequences
//   with U+FFFD).
// - The returned TString is heap-allocated and independent of the input.
TH_EXPORT struct TString tstr_utf16_to_utf8(struct TString utf16_str);

// Concatenates two UTF-16 TString objects.
//
// # Parameters
// - `count`: The number of strings to concatenate.
// - `tstr_list`: An array of TString objects to concatenate.
//
// # Returns
// - A new TString object containing the concatenated result.
//
// # Notes
// - The returned TString must be freed using `tstr_drop`.
TH_EXPORT struct TString tstr_concat_utf16(size_t count, struct TString const *tstr_list);

// Extracts a substring from a UTF-16 TString object.
//
// # Parameters
// - `tstr`: The source TString object to extract the substring from.
// - `pos`: The starting position of the substring within the source TString
//   object.
// - `len`: The length of the substring to extract.
//
// # Returns
// - A TString reference of the extracted substring.
//
// # Notes
// - The returned TString is just a view of the original string and does not own
//   the memory, so it should not be freed.
TH_EXPORT struct TString tstr_substr_utf16(struct TString tstr, size_t pos, size_t len);

#endif  // TAIHE_STRING_ABI_H
