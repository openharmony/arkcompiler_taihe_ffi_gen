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
    TSTRING_STORAGE_MASK = 0xFFFF,
    TSTRING_STORAGE_STATIC = 0u,
    TSTRING_STORAGE_INTERNAL = 1u,
    TSTRING_STORAGE_EXTERNAL = 2u,
    TSTRING_STORAGE_BORROWED = 3u,

    TSTRING_ENCODING_MASK = 0xFFFF0000,
    TSTRING_ENCODING_UNKNOWN = 0u << 16,
    TSTRING_ENCODING_UTF8 = 1u << 16,
    TSTRING_ENCODING_UTF16 = 2u << 16,
};

struct TStringControlBlock {
    TRefCount ref_count;
    void (*drop)(void *);
    void *context;
};

struct TString {
    void const *data;
    uint32_t byte_length;
    uint32_t flags;
    struct TStringControlBlock *cb;
};

//////////////////
// Public C API //
//////////////////

// Returns the UTF8 buffer.
TH_INLINE const char *tstr_buf_utf8(struct TString tstr)
{
    return (char const *)tstr.data;
}

// Returns the UTF16 buffer.
TH_INLINE const uint16_t *tstr_buf_utf16(struct TString tstr)
{
    return (uint16_t const *)tstr.data;
}

// Returns the UTF8 length in bytes.
TH_INLINE size_t tstr_len_utf8(struct TString tstr)
{
    return tstr.byte_length / sizeof(char);
}

// Returns the UTF16 length in code units.
TH_INLINE size_t tstr_len_utf16(struct TString tstr)
{
    return tstr.byte_length / sizeof(uint16_t);
}

// Returns whether the TString is empty.
TH_INLINE uint32_t tstr_empty(struct TString tstr)
{
    return tstr.byte_length == 0;
}

// Returns the TString encoding.
TH_INLINE uint32_t tstr_encoding(struct TString tstr)
{
    return tstr.flags & TSTRING_ENCODING_MASK;
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

// Allocates memory and initializes a UTF8 TString with a given capacity.
//
// # Arguments
// - `tstr_ptr`: Pointer to an uninitialized TString structure.
// - `capacity`: The desired capacity of the string buffer, in bytes.
//
// # Returns
// - Pointer to the allocated buffer, or `NULL` if allocation fails.
//
// # Notes
// - The caller is responsible for setting the string length.
// - Reference count is set to 1 after called.
TH_EXPORT char *tstr_initialize_utf8(struct TString *tstr_ptr, size_t capacity);

// Allocates memory and initializes a UTF16 TString with a given capacity.
//
// # Arguments
// - `tstr_ptr`: Pointer to an uninitialized TString structure.
// - `capacity`: The desired capacity of the string buffer, in UTF16 code units.
//
// # Returns
// - Pointer to the allocated buffer, or `NULL` if allocation fails.
//
// # Notes
// - The caller is responsible for setting the string length.
// - Reference count is set to 1 after called.
TH_EXPORT uint16_t *tstr_initialize_utf16(struct TString *tstr_ptr, size_t capacity);

// Creates a new heap-allocated TString by copying an existing UTF8 string.
//
// # Arguments
// - `buf`: Pointer to the UTF8 buffer to copy. Null pointer is invalid.
// - `len`: The length of the string in bytes.
//
// # Returns
// - A new TString containing a copy of `buf`, or an invalid TString if
//   allocation fails.
//
// # Notes
// - Exactly `len` bytes are copied from `buf`.
// - The returned TString must be released using `tstr_drop`.
TH_EXPORT struct TString tstr_new_utf8(char const *buf TH_NONNULL, size_t len);

// Creates a new heap-allocated TString by copying an existing UTF16 string.
//
// # Arguments
// - `buf`: Pointer to the UTF16 buffer to copy. Null pointer is invalid.
// - `len`: The length of the string in UTF16 code units.
//
// # Returns
// - A new TString containing a copy of `buf`, or an invalid TString if
//   allocation fails.
//
// # Notes
// - Exactly `len` UTF16 code units are copied from `buf`.
// - The returned TString must be released using `tstr_drop`.
TH_EXPORT struct TString tstr_new_utf16(uint16_t const *buf TH_NONNULL, size_t len);

// Creates a non-owning TString reference from an existing UTF8 buffer.
//
// # Arguments
// - `buf`: Pointer to the UTF8 buffer. Null pointer is invalid.
// - `len`: The length of the string in bytes.
//
// # Returns
// - A TString referencing `buf`.
//
// # Notes
// - The returned TString does not own the buffer.
// - The caller must keep `buf` valid and unchanged during the lifetime of the
//   returned TString.
// - `tstr_drop` has no effect on the referenced buffer.
TH_EXPORT struct TString tstr_new_borrowed_utf8(char const *buf TH_NONNULL, size_t len);

// Creates a non-owning TString reference from an existing UTF16 buffer.
//
// # Arguments
// - `buf`: Pointer to the UTF16 buffer. Null pointer is invalid.
// - `len`: The length of the string in UTF16 code units.
//
// # Returns
// - A TString referencing `buf`.
//
// # Notes
// - The returned TString does not own the buffer.
// - The caller must keep `buf` valid and unchanged during the lifetime of the
//   returned TString.
// - `tstr_drop` has no effect on the referenced buffer.
TH_EXPORT struct TString tstr_new_borrowed_utf16(uint16_t const *buf TH_NONNULL, size_t len);

// Creates a TString from an external UTF8 buffer with a custom drop callback.
//
// # Arguments
// - `buf`: Pointer to the UTF8 buffer. Null pointer is invalid.
// - `len`: The length of the string in bytes.
// - `context`: External object passed to `drop`.
// - `drop`: Callback invoked when the TString is finally released.
//
// # Returns
// - A TString referencing `buf`, or an invalid TString if allocation fails.
//
// # Notes
// - The returned TString does not copy `buf`.
// - The caller must ensure `buf` remains valid until `drop` is called.
TH_EXPORT struct TString tstr_new_from_external_utf8(char const *buf TH_NONNULL, size_t len, void *context,
                                                     void (*drop)(void *));

// Creates a TString from an external UTF16 buffer with a custom drop callback.
//
// # Arguments
// - `buf`: Pointer to the UTF16 buffer. Null pointer is invalid.
// - `len`: The length of the string in UTF16 code units.
// - `context`: External object passed to `drop`.
// - `drop`: Callback invoked when the TString is finally released.
//
// # Returns
// - A TString referencing `buf`, or an invalid TString if allocation fails.
//
// # Notes
// - The returned TString does not copy `buf`.
// - The caller must ensure `buf` remains valid until `drop` is called.
TH_EXPORT struct TString tstr_new_from_external_utf16(uint16_t const *buf TH_NONNULL, size_t len, void *context,
                                                      void (*drop)(void *));

// Creates a TString from a static UTF16 buffer.
//
// # Arguments
// - `buf`: Pointer to the UTF16 buffer. Null pointer is invalid.
// - `len`: The length of the string in UTF16 code units.
//
// # Returns
// - A TString referencing `buf`.
//
// # Notes
// - The returned TString does not own the buffer.
// - `buf` must remain valid for the required lifetime.
TH_EXPORT struct TString tstr_new_from_static_utf16(uint16_t const *buf TH_NONNULL, size_t len);

// Creates a TString from a static UTF8 buffer.
//
// # Arguments
// - `buf`: Pointer to the UTF8 buffer. Null pointer is invalid.
// - `len`: The length of the string in bytes.
//
// # Returns
// - A TString referencing `buf`.
//
// # Notes
// - The returned TString does not own the buffer.
// - `buf` must remain valid for the required lifetime.
TH_EXPORT struct TString tstr_new_from_static_utf8(char const *buf TH_NONNULL, size_t len);

// Frees a TString, releasing allocated memory if applicable.
//
// # Arguments
// - `tstr`: The TString to be freed.
//
// # Notes
// - Static and reference TStrings are not freed.
// - Native and external TStrings are reference-counted.
TH_EXPORT void tstr_drop(struct TString tstr);

// Creates a duplicate of a TString.
//
// # Arguments
// - `tstr`: The TString to be copied.
//
// # Returns
// - A duplicated TString, or an invalid TString if duplication fails.
//
// # Notes
// - If `tstr` is a reference, a new heap-allocated copy is created.
// - If `tstr` is native or external, its reference count is incremented.
// - If `tstr` is static, it is returned as is.
// - Use `tstr_drop` to release the duplicate when done.
TH_EXPORT struct TString tstr_dup(struct TString tstr);

// Creates a duplicate of a TString, converting it to UTF8 encoding if necessary.
//
// # Parameters
// - `tstr`: The source TString.
//
// # Returns
// - A TString encoded in UTF8, or an invalid TString on failure.
//
// # Notes
// - If `tstr` is already UTF8, this function behaves like `tstr_dup`.
// - Invalid UTF16 surrogate pairs are replaced with U+FFFD during conversion.
// - Use `tstr_drop` to release the returned TString when done.
TH_EXPORT struct TString tstr_dup_as_utf8(struct TString tstr);

// Creates a duplicate of a TString, converting it to UTF16 encoding if necessary.
//
// # Parameters
// - `tstr`: The source TString.
//
// # Returns
// - A TString encoded in UTF16, or an invalid TString on failure.
//
// # Notes
// - If `tstr` is already UTF16, this function behaves like `tstr_dup`.
// - Malformed UTF8 sequences may be replaced with U+FFFD or cause conversion
//   failure according to the internal conversion policy.
// - Use `tstr_drop` to release the returned TString when done.
TH_EXPORT struct TString tstr_dup_as_utf16(struct TString tstr);

// Concatenates TString objects and returns a new TString in UTF8 encoding.
//
// # Parameters
// - `count`: The number of strings to concatenate.
// - `tstr_list`: An array of TString objects to concatenate.
//
// # Returns
// - A new TString object containing the concatenated result, or an invalid
//   TString on failure.
//
// # Notes
// - UTF16 inputs are converted to UTF8.
// - The returned TString must be released using `tstr_drop`.
TH_EXPORT struct TString tstr_concat_as_utf8(size_t count, struct TString const *tstr_list);

// Concatenates TString objects and returns a new TString in UTF16 encoding.
//
// # Parameters
// - `count`: The number of strings to concatenate.
// - `tstr_list`: An array of TString objects to concatenate.
//
// # Returns
// - A new TString object containing the concatenated result, or an invalid
//   TString on failure.
//
// # Notes
// - UTF8 inputs are converted to UTF16.
// - The returned TString must be released using `tstr_drop`.
TH_EXPORT struct TString tstr_concat_as_utf16(size_t count, struct TString const *tstr_list);

// Extracts a substring from a UTF8 TString object.
//
// # Parameters
// - `tstr`: The source TString object to extract the substring from.
// - `pos`: The starting byte position of the substring.
// - `len`: The length of the substring in bytes.
//
// # Returns
// - A TString view of the extracted substring, or an invalid TString if `tstr`
//   is not UTF8.
//
// # Notes
// - The returned TString is a temporary non-owning view of the original string.
// - The caller must keep the original storage valid while using the returned
//   TString.
// - Call `tstr_dup` to create an owning copy if needed.
TH_EXPORT struct TString tstr_substr_utf8(struct TString tstr, size_t pos, size_t len);

// Extracts a substring from a UTF16 TString object.
//
// # Parameters
// - `tstr`: The source TString object to extract the substring from.
// - `pos`: The starting position of the substring in UTF16 code units.
// - `len`: The length of the substring in UTF16 code units.
//
// # Returns
// - A TString view of the extracted substring, or an invalid TString if `tstr`
//   is not UTF16.
//
// # Notes
// - The returned TString is a temporary non-owning view of the original string.
// - The caller must keep the original storage valid while using the returned
//   TString.
// - Call `tstr_dup` to create an owning copy if needed.
TH_EXPORT struct TString tstr_substr_utf16(struct TString tstr, size_t pos, size_t len);

#endif  // TAIHE_STRING_ABI_H
