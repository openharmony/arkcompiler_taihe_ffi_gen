#pragma once
#include <stddef.h>
#include <stdint.h>

#include "common.h"

/////////////////////////////////////////
// Private ABI: Don't use in your code //
/////////////////////////////////////////

enum TStringFlags {
  TSTRING_SHARED = 1,
};

struct TString {
  uint32_t flags;
  uint32_t length;
  char const* ptr;  // Always valid and non-null.
};

struct TStringHeap {
  struct TString header;
  TRefCount count;
  char buffer[1];
};

//////////////////
// Public C API //
//////////////////

/// Returns the buffer of the TString.
inline const char* tstr_buf(const struct TString* s) { return s->ptr; }

/// Returns the length of the TString.
inline size_t tstr_len(const struct TString* s) { return s->length; }

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
inline struct TString* tstr_new_ref(const char* buf TH_NONNULL, size_t len,
                                    struct TString* tstr) {
  if (len > UINT32_MAX) return NULL;
  if (buf[len] != '\0') return NULL;

  tstr->flags = TSTRING_SHARED;
  tstr->length = len;
  tstr->ptr = buf;
  return tstr;
}

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
const struct TString* tstr_new(const char* buf TH_NONNULL, size_t len);

// Frees the string. The string should not be accessed thereafter.
void tstr_drop(struct TString* s);

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
const struct TString* tstr_dup(struct TString* s);
