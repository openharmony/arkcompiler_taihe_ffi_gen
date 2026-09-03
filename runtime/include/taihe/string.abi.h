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

#ifndef TSTR_ENABLE_RETAINABLE_SUBSTR
#define TSTR_ENABLE_RETAINABLE_SUBSTR 1
#endif

/////////////////////////////////////////
// Private ABI: Don't use in your code //
/////////////////////////////////////////

// Storage modes are private duplication strategies. They do not determine a
// TString value's public ownership or drop responsibility.
enum TStringFlags {
    TSTRING_STORAGE_MASK = 0xFFFF,
    TSTRING_STORAGE_INVALID = 0u,
    TSTRING_STORAGE_STATIC = 1u,
    TSTRING_STORAGE_INTERNAL = 2u,
    TSTRING_STORAGE_ACQUIRED = 4u,
    TSTRING_STORAGE_ACQUIRABLE_BORROWED = 8u,
    TSTRING_STORAGE_COPIABLE_BORROWED = 16u,

    TSTRING_ENCODING_MASK = 0xFFFF0000,
    TSTRING_ENCODING_UNKNOWN = 0u << 16,
    TSTRING_ENCODING_UTF8 = 1u << 16,
    TSTRING_ENCODING_UTF16 = 2u << 16,
};

// An acquired reference that keeps an external buffer alive. Ownership of the
// reference is transferred with this structure and released at most once.
struct TStringGlobalRefContext {
    void *ref;
    void (*release)(void *);
};

// A local reference that can be acquired to produce an independently owned
// global reference. Calling acquire does not transfer ownership of the local
// reference itself.
struct TStringLocalRefContext {
    void *ref;
    struct TStringGlobalRefContext (*acquire)(void *);
};

struct TStringInternalControlBlock {
    TRefCount ref_count;
};

struct TStringAcquiredControlBlock {
    TRefCount ref_count;
    struct TStringGlobalRefContext global_ctx;
};

// Lazily caches one acquired control block. The cache is initialized exactly
// once by tstr_new_acquirable_borrowed_utf8/utf16 and must later be passed
// exactly once to tstr_acquire_cache_drop.
struct TStringAcquireCache {
    struct TStringAcquiredControlBlock *acquired_cb;
    struct TStringLocalRefContext local_ctx;
};

struct TStringCopyCache;

struct TString {
    uint32_t flags;
    uint32_t byte_length;
    void const *data;

    union {
        struct TStringInternalControlBlock *internal_cb;
        struct TStringAcquiredControlBlock *acquired_cb;
        struct TStringAcquireCache *acquire_cache;
        struct TStringCopyCache *copy_cache;  // NULLABLE
    };
};

// Lazily caches one owning copy of the original borrowed string. The cache is
// initialized exactly once by a function that accepts it and must later be
// passed exactly once to tstr_copy_cache_drop.
struct TStringCopyCache {
    struct TString copied;
    struct TString original;
};

//////////////////
// Public C API //
//////////////////

TH_INLINE uint32_t tstr_encoding(struct TString tstr)
{
    return tstr.flags & TSTRING_ENCODING_MASK;
}

TH_INLINE const void *tstr_data(struct TString tstr)
{
    return tstr.data;
}

TH_INLINE const char *tstr_buf_utf8(struct TString tstr)
{
    return (char const *)tstr_data(tstr);
}

TH_INLINE const uint16_t *tstr_buf_utf16(struct TString tstr)
{
    return (uint16_t const *)tstr_data(tstr);
}

TH_INLINE size_t tstr_byte_length(struct TString tstr)
{
    return tstr.byte_length;
}

TH_INLINE size_t tstr_len_utf8(struct TString tstr)
{
    return tstr_byte_length(tstr) / sizeof(char);
}

TH_INLINE size_t tstr_len_utf16(struct TString tstr)
{
    return tstr_byte_length(tstr) / sizeof(uint16_t);
}

TH_INLINE uint32_t tstr_is_empty(struct TString tstr)
{
    return tstr_byte_length(tstr) == 0;
}

// API lifetime semantics:
// - A holder is an independent value and must be passed exactly once to
//   tstr_drop, including when it is invalid.
// - A borrowed view has no drop responsibility and must not outlive the buffer,
//   cache, or other resource on which it depends.

// Creates an invalid holder.
//
// # Returns
// - An invalid holder.
//
// # Notes
// - The returned holder can be treated as both holder and view.
TH_EXPORT struct TString tstr_new_invalid();

// Creates a static value from a UTF8 buffer.
//
// # Arguments
// - `buf`: Pointer to a static UTF8 buffer. Null pointer is invalid.
// - `len`: The length of the string in bytes.
//
// # Returns
// - A static value referencing `buf`.
//
// # Notes
// - The returned value can be treated as both holder and view.
TH_EXPORT struct TString tstr_new_static_utf8(char const *buf TH_NONNULL, size_t len);

// Creates a static value from a UTF16 buffer.
//
// # Arguments
// - `buf`: Pointer to a static UTF16 buffer. Null pointer is invalid.
// - `len`: The length of the string in UTF16 code units.
//
// # Returns
// - A static value referencing `buf`.
//
// # Notes
// - The returned value can be treated as both holder and view.
TH_EXPORT struct TString tstr_new_static_utf16(uint16_t const *buf TH_NONNULL, size_t len);

// Creates a holder from an acquired external UTF8 buffer.
//
// # Arguments
// - `buf`: Pointer to the UTF8 buffer. Null pointer is invalid.
// - `len`: The length of the string in bytes.
// - `ctx`: Acquired global reference whose ownership is transferred to the
//   function.
//
// # Returns
// - A holder referencing `buf`, or an invalid holder if allocation fails.
//
// # Notes
// - The function consumes `ctx` on both success and failure.
// - The buffer must remain valid until ctx.release is called.
TH_EXPORT struct TString tstr_new_acquired_utf8(char const *buf TH_NONNULL, size_t len,
                                                struct TStringGlobalRefContext ctx);

// Creates a holder from an acquired external UTF16 buffer.
//
// # Arguments
// - `buf`: Pointer to the UTF16 buffer. Null pointer is invalid.
// - `len`: The length of the string in UTF16 code units.
// - `ctx`: Acquired global reference whose ownership is transferred to the
//   function.
//
// # Returns
// - A holder referencing `buf`, or an invalid holder if allocation fails.
//
// # Notes
// - The function consumes `ctx` on both success and failure.
// - The buffer must remain valid until ctx.release is called.
TH_EXPORT struct TString tstr_new_acquired_utf16(uint16_t const *buf TH_NONNULL, size_t len,
                                                 struct TStringGlobalRefContext ctx);

// Creates an acquirable borrowed view of an external UTF8 buffer.
//
// # Arguments
// - `buf`: Pointer to the UTF8 buffer. Null pointer is invalid.
// - `len`: The length of the string in bytes.
// - `ctx`: Local reference used to acquire a global reference that keeps `buf`
//   alive.
// - `cache`: Uninitialized acquire cache shared by views derived from the
//   result. Null pointer is invalid.
//
// # Returns
// - A borrowed view referencing `buf`.
//
// # Notes
// - `cache` is initialized exactly once with `ctx` and must eventually be
//   passed exactly once to tstr_acquire_cache_drop.
// - The view and its derived borrowed views must not outlive `buf` or `cache`.
//   The local reference must remain valid until the first duplication acquires
//   the global reference, or until all dependent views end if none does.
TH_EXPORT struct TString tstr_new_acquirable_borrowed_utf8(char const *buf TH_NONNULL, size_t len,
                                                           struct TStringAcquireCache *cache TH_NONNULL,
                                                           struct TStringLocalRefContext ctx);

// Creates an acquirable borrowed view of an external UTF16 buffer.
//
// # Arguments
// - `buf`: Pointer to the UTF16 buffer. Null pointer is invalid.
// - `len`: The length of the string in UTF16 code units.
// - `ctx`: Local reference used to acquire a global reference that keeps `buf`
//   alive.
// - `cache`: Uninitialized acquire cache shared by views derived from the
//   result. Null pointer is invalid.
//
// # Returns
// - A borrowed view referencing `buf`.
//
// # Notes
// - `cache` is initialized exactly once with `ctx` and must eventually be
//   passed exactly once to tstr_acquire_cache_drop.
// - The view and its derived borrowed views must not outlive `buf` or `cache`.
//   The local reference must remain valid until the first duplication acquires
//   the global reference, or until all dependent views end if none does.
TH_EXPORT struct TString tstr_new_acquirable_borrowed_utf16(uint16_t const *buf TH_NONNULL, size_t len,
                                                            struct TStringAcquireCache *cache TH_NONNULL,
                                                            struct TStringLocalRefContext ctx);

// Creates a copyable borrowed view of an existing UTF8 buffer.
//
// # Arguments
// - `buf`: Pointer to the UTF8 buffer. Null pointer is invalid.
// - `len`: The length of the string in bytes.
// - `cache`: Optional uninitialized copy cache shared by views derived from the
//   result.
//
// # Returns
// - A borrowed view referencing `buf`.
//
// # Notes
// - If `cache` is null, each tstr_dup copies the referenced range directly.
// - If `cache` is nonnull, it is initialized exactly once and must eventually
//   be passed exactly once to tstr_copy_cache_drop.
// - The view and its derived borrowed views must not outlive `buf` or `cache`.
//   Keep `buf` valid and unchanged while any such view may read it or duplicate
//   through a cache that has not materialized its copy.
TH_EXPORT struct TString tstr_new_copyable_borrowed_utf8(char const *buf TH_NONNULL, size_t len,
                                                         struct TStringCopyCache *cache);

// Creates a copyable borrowed view of an existing UTF16 buffer.
//
// # Arguments
// - `buf`: Pointer to the UTF16 buffer. Null pointer is invalid.
// - `len`: The length of the string in UTF16 code units.
// - `cache`: Optional uninitialized copy cache shared by views derived from the
//   result.
//
// # Returns
// - A borrowed view referencing `buf`.
//
// # Notes
// - If `cache` is null, each tstr_dup copies the referenced range directly.
// - If `cache` is nonnull, it is initialized exactly once and must eventually
//   be passed exactly once to tstr_copy_cache_drop.
// - The view and its derived borrowed views must not outlive `buf` or `cache`.
//   Keep `buf` valid and unchanged while any such view may read it or duplicate
//   through a cache that has not materialized its copy.
TH_EXPORT struct TString tstr_new_copyable_borrowed_utf16(uint16_t const *buf TH_NONNULL, size_t len,
                                                          struct TStringCopyCache *cache);

// Extracts a substring from a UTF8 TString object.
//
// # Parameters
// - `tstr`: The source TString object to extract the substring from.
// - `pos`: The starting byte position of the substring.
// - `len`: The length of the substring in bytes.
// - `cache`: Optional uninitialized copy cache for the result.
//
// # Returns
// - A borrowed view of the selected range, or an invalid borrowed view if
//   `tstr` is not UTF8 or `pos` is out of range.
//
// # Notes
// - The result and its derived borrowed views must not outlive the source
//   buffer or any cache they reference.
// - If `cache` is nonnull, it is initialized exactly once and must eventually
//   be passed exactly once to tstr_copy_cache_drop.
TH_EXPORT struct TString tstr_substr_utf8(struct TString tstr, size_t pos, size_t len, struct TStringCopyCache *cache);

// Extracts a substring from a UTF16 TString object.
//
// # Parameters
// - `tstr`: The source TString object to extract the substring from.
// - `pos`: The starting position of the substring in UTF16 code units.
// - `len`: The length of the substring in UTF16 code units.
// - `cache`: Optional uninitialized copy cache for the result.
//
// # Returns
// - A borrowed view of the selected range, or an invalid borrowed view if
//   `tstr` is not UTF16 or `pos` is out of range.
//
// # Notes
// - The result and its derived borrowed views must not outlive the source
//   buffer or any cache they reference.
// - If `cache` is nonnull, it is initialized exactly once and must eventually
//   be passed exactly once to tstr_copy_cache_drop.
TH_EXPORT struct TString tstr_substr_utf16(struct TString tstr, size_t pos, size_t len, struct TStringCopyCache *cache);

// Creates a holder from a TString value.
//
// # Arguments
// - `tstr`: The TString to be copied.
//
// # Returns
// - An independent holder, or an invalid holder if duplication fails.
//
// # Notes
// - Any cache referenced by a borrowed input must remain valid for this call.
TH_EXPORT struct TString tstr_dup(struct TString tstr);

// Fulfills the drop responsibility of one holder.
//
// # Arguments
// - `tstr`: The holder whose responsibility is consumed.
//
// # Notes
// - This function consumes holders only. It must not be used for a borrowed
//   view that shares holder state, such as a substring result. Other borrowed
//   views hold no resource, so passing them is unnecessary.
// - Dropping an invalid or static holder releases no resource.
TH_EXPORT void tstr_drop(struct TString tstr);

// Fulfills the drop responsibility of a copy cache.
//
// The cache must have been initialized exactly once and must be dropped exactly
// once after all borrowed views that depend on it have ended their lifetimes.
TH_EXPORT void tstr_copy_cache_drop(struct TStringCopyCache const *cache TH_NONNULL);

// Fulfills the drop responsibility of an acquire cache.
//
// The cache must have been initialized exactly once and must be dropped exactly
// once after all borrowed views that depend on it have ended their lifetimes.
TH_EXPORT void tstr_acquire_cache_drop(struct TStringAcquireCache const *cache TH_NONNULL);

// Creates a holder by copying a UTF8 string.
//
// # Arguments
// - `buf`: Pointer to the UTF8 buffer to copy. Null pointer is invalid.
// - `len`: The length of the string in bytes.
//
// # Returns
// - A holder containing a copy of `buf`, or an invalid holder if allocation
//   fails.
//
// # Notes
// - Exactly `len` bytes are copied from `buf`.
TH_EXPORT struct TString tstr_new_copied_utf8(char const *buf TH_NONNULL, size_t len);

// Creates a holder by copying a UTF16 string.
//
// # Arguments
// - `buf`: Pointer to the UTF16 buffer to copy. Null pointer is invalid.
// - `len`: The length of the string in UTF16 code units.
//
// # Returns
// - A holder containing a copy of `buf`, or an invalid holder if allocation
//   fails.
//
// # Notes
// - Exactly `len` UTF16 code units are copied from `buf`.
TH_EXPORT struct TString tstr_new_copied_utf16(uint16_t const *buf TH_NONNULL, size_t len);

// Creates a duplicate of a TString, converting it to UTF8 encoding if necessary.
//
// # Parameters
// - `tstr`: The source TString.
//
// # Returns
// - A UTF8 holder, or an invalid holder on failure.
//
// # Notes
// - Invalid UTF16 surrogate pairs are replaced with U+FFFD during conversion.
TH_EXPORT struct TString tstr_dup_as_utf8(struct TString tstr);

// Creates a duplicate of a TString, converting it to UTF16 encoding if necessary.
//
// # Parameters
// - `tstr`: The source TString.
//
// # Returns
// - A UTF16 holder, or an invalid holder on failure.
//
// # Notes
// - Invalid UTF8 sequences are replaced with U+FFFD during conversion.
TH_EXPORT struct TString tstr_dup_as_utf16(struct TString tstr);

// Concatenates TString objects and returns a new TString in UTF8 encoding.
//
// # Parameters
// - `count`: The number of strings to concatenate.
// - `tstr_list`: An array of TString objects to concatenate.
//
// # Returns
// - A UTF8 holder containing the result, or an invalid holder on failure.
//
// # Notes
// - UTF16 inputs are converted to UTF8.
TH_EXPORT struct TString tstr_concat_as_utf8(size_t count, struct TString const *tstr_list);

// Concatenates TString objects and returns a new TString in UTF16 encoding.
//
// # Parameters
// - `count`: The number of strings to concatenate.
// - `tstr_list`: An array of TString objects to concatenate.
//
// # Returns
// - A UTF16 holder containing the result, or an invalid holder on failure.
//
// # Notes
// - UTF8 inputs are converted to UTF16.
TH_EXPORT struct TString tstr_concat_as_utf16(size_t count, struct TString const *tstr_list);

#endif  // TAIHE_STRING_ABI_H
