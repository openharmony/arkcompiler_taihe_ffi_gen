#pragma once
#include <stddef.h>
#include <stdint.h>

#include "common.h"

/////////////////////////////////////////
// Private ABI: Don't use in your code //
/////////////////////////////////////////

enum TStringFlags {
  TSTRING_REF = 1,
};

struct TString {
  uint32_t flags;
  uint32_t length;
  char const* ptr;  // Always valid and non-null.
};

struct TStringData {
  TRefCount count;
  char buffer[];
};

//////////////////
// Public C API //
//////////////////

/// Returns the buffer of the TString.
TH_INLINE const char* tstr_buf(struct TString tstr) {
  return tstr.ptr;
}

/// Returns the length of the TString.
TH_INLINE size_t tstr_len(struct TString tstr) {
  return tstr.length;
}

// Creates a TString from an existing string.
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
TH_INLINE struct TString tstr_new_ref(const char* buf TH_NONNULL, size_t len) {
  struct TString tstr;
  tstr.flags = TSTRING_REF;
  tstr.length = len;
  tstr.ptr = buf;
  return tstr;
}

char *tstr_initialize(struct TString *tstr_ptr, uint32_t capacity);

/// Creates a heap-allocated TString by copying the original string.
//
// # Arguments
// - `buf`: a null-terminated string. Null pointer is invalid.
// - `len`: the length of the string.
//
// # Returns
// - `tstr`, if the string is created successfully.
// - `NULL`, if the string is not null-terminated, or the length is too large,
//    or the system is out of memory. In this case, the original `tstr` is still
//    uninitialized and should not be used.
//
// # Notes
// Free the TString with `tstr_drop` after use.
TH_EXPORT struct TString tstr_new(const char* buf TH_NONNULL, size_t len);

// Frees the string. The string should not be accessed thereafter.
TH_EXPORT void tstr_drop(struct TString tstr);

// Copies a TString.
//
// # Returns
// - `tstr`, if the string is created successfully.
// - `NULL`, on insufficient memory.
//
// # Notes
// - If string was created by `tstr_new`, the reference count of the backing
//   buffer is incremented.
// - If string was created by `tstr_new_ref`, the source string is copied
//   to a new heap-allocated buffer and is managed by reference counting.
// - Similar to `tstr_new`, remeber to call `tstr_drop` after use.
TH_EXPORT struct TString tstr_dup(struct TString tstr);

// Concatenates two TString objects.
//
// # Returns
// - `tstr`, if the concatenation is successful.
// - `NULL`, on insufficient memory.
//
// # Notes
// - The resulting TString object contains the concatenation of `left` and `right`.
// - The reference counts of both `left` and `right` are incremented. 
//   Remember to call `tstr_drop` after use to manage memory correctly.
TH_EXPORT struct TString tstr_concat(struct TString left, struct TString right);

// Extracts a substring from a TString object.
//
// # Parameters
// - `s`: The source TString object to extract the substring from.
// - `pos`: The starting position of the substring within the source TString object. 
// - `len`: The length of the substring to extract.
//
// # Returns
// - `tstr`, if the substring extraction is successful.
// - `NULL`, on insufficient memory, if `pos` is out of bounds, or if `len` extends beyond the end of the source TString object.
//
// # Notes
// - The resulting TString object is a substring of `s` starting from `pos` with a length of `len`.
// - Remember to call `tstr_drop` after use to manage memory correctly.
TH_EXPORT struct TString tstr_substr(struct TString tstr, size_t pos, size_t len);
