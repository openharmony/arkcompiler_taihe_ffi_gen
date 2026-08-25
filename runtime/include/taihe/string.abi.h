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

#ifndef TSTR_ENABLE_STRING_SSO
#define TSTR_ENABLE_STRING_SSO 1
#endif

#ifndef TSTR_ENABLE_RETAINABLE_SUBSTR
#define TSTR_ENABLE_RETAINABLE_SUBSTR 1
#endif

/////////////////////////////////////////
// Private ABI: Don't use in your code //
/////////////////////////////////////////

enum TStringFlags {
    TSTRING_STORAGE_MASK = 0xFFFF,
    TSTRING_STORAGE_INVALID = 0u,
    TSTRING_STORAGE_STATIC = 1u,
    TSTRING_STORAGE_INTERNAL = 2u,
    TSTRING_STORAGE_EXTERNAL = 4u,
    TSTRING_STORAGE_BORROWED = 8u,
#if TSTR_ENABLE_STRING_SSO
    TSTRING_STORAGE_SMALL = 16u,
#endif

    TSTRING_ENCODING_MASK = 0xFFFF0000,
    TSTRING_ENCODING_UNKNOWN = 0u << 16,
    TSTRING_ENCODING_UTF8 = 1u << 16,
    TSTRING_ENCODING_UTF16 = 2u << 16,
};

struct TStringInternalControlBlock {
    TRefCount ref_count;
};

struct TStringExternalControlBlock {
    TRefCount ref_count;
    void (*drop)(void *);
    void *context;
};

#if TSTR_ENABLE_STRING_SSO
#define TSTR_SMALL_UTF8_CAPACITY (sizeof(void *) * 2 / sizeof(char))
#define TSTR_SMALL_UTF16_CAPACITY (sizeof(void *) * 2 / sizeof(uint16_t))
#define TSTR_SMALL_UTF8_MAX_LENGTH (TSTR_SMALL_UTF8_CAPACITY - 1)
#define TSTR_SMALL_UTF16_MAX_LENGTH (TSTR_SMALL_UTF16_CAPACITY - 1)
#endif

struct TString {
    uint32_t flags;
    uint32_t byte_length;
#if TSTR_ENABLE_STRING_SSO
    union {
        struct {
#endif
            void const *data;

            union {
                struct TStringInternalControlBlock *cb_int;
                struct TStringExternalControlBlock *cb_ext;
            };
#if TSTR_ENABLE_STRING_SSO
        };

        char small_utf8[TSTR_SMALL_UTF8_CAPACITY];
        uint16_t small_utf16[TSTR_SMALL_UTF16_CAPACITY];
    };
#endif
};

//////////////////
// Public C API //
//////////////////

// Returns the TString encoding.
TH_INLINE uint32_t tstr_encoding(struct TString tstr)
{
    return tstr.flags & TSTRING_ENCODING_MASK;
}

// Returns the TString storage type.
TH_INLINE uint32_t tstr_mode(struct TString tstr)
{
    return tstr.flags & TSTRING_STORAGE_MASK;
}

// Check if the TString is valid.
TH_INLINE uint32_t tstr_valid(struct TString tstr)
{
    return tstr_mode(tstr) != TSTRING_STORAGE_INVALID;
}

// Sets the TString mode to invalid.
TH_INLINE void tstr_set_invalid(struct TString *tstr_ptr)
{
    tstr_ptr->flags = (tstr_ptr->flags & ~TSTRING_STORAGE_MASK) | TSTRING_STORAGE_INVALID;
}

// Returns the UTF8 buffer.
TH_INLINE const char *tstr_buf_utf8(struct TString const *tstr)
{
#if TSTR_ENABLE_STRING_SSO
    return tstr_mode(*tstr) == TSTRING_STORAGE_SMALL ? tstr->small_utf8 : (char const *)tstr->data;
#else
    return (char const *)tstr->data;
#endif
}

// Returns the UTF16 buffer.
TH_INLINE const uint16_t *tstr_buf_utf16(struct TString const *tstr)
{
#if TSTR_ENABLE_STRING_SSO
    return tstr_mode(*tstr) == TSTRING_STORAGE_SMALL ? tstr->small_utf16 : (uint16_t const *)tstr->data;
#else
    return (uint16_t const *)tstr->data;
#endif
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
// - `drop`: Callback to release the external buffer.
//
// # Returns
// - A TString referencing `buf`, or an invalid TString if allocation fails.
//
// # Notes
// - The caller must ensure `buf` remains valid until `drop` is called.
// - It is not guaranteed that the returned TString is in external mode.
// - If creation fails or a non-external TString is created, `drop` will be called
//   directly.
TH_EXPORT struct TString tstr_new_from_external_utf8(char const *buf TH_NONNULL, size_t len, void *context,
                                                     void (*drop)(void *));

// Creates a TString from an external UTF16 buffer with a custom drop callback.
//
// # Arguments
// - `buf`: Pointer to the UTF16 buffer. Null pointer is invalid.
// - `len`: The length of the string in UTF16 code units.
// - `context`: External object passed to `drop`.
// - `drop`: Callback to release the external buffer.
//
// # Returns
// - A TString referencing `buf`, or an invalid TString if allocation fails.
//
// # Notes
// - The caller must ensure `buf` remains valid until `drop` is called.
// - It is not guaranteed that the returned TString is in external mode.
// - If creation fails or a non-external TString is created, `drop` will be called
//   directly.
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
// - Invalid UTF8 sequences are replaced with U+FFFD during conversion.
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
// - The result has an EXTRINSIC VIEW TYPESTATE regardless of its runtime storage
//   mode.
// - The caller must keep the source storage valid while using the result.
// - No ownership reference is acquired for the result. Do not pass it directly
//   to `tstr_drop`.
// - Use `tstr_dup` to create an independently retainable TString.
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
// - The result has an EXTRINSIC VIEW TYPESTATE regardless of its runtime storage
//   mode.
// - The caller must keep the source storage valid while using the result.
// - No ownership reference is acquired for the result. Do not pass it directly
//   to `tstr_drop`.
// - Use `tstr_dup` to create an independently retainable TString.
TH_EXPORT struct TString tstr_substr_utf16(struct TString tstr, size_t pos, size_t len);

#endif  // TAIHE_STRING_ABI_H
