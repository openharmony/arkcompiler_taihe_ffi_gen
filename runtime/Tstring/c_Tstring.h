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
  char const* ptr;
};

// Shared HSTRING header with reference counting
struct TStringHeap {
  struct TString header;
  TRefCount count;
  char buffer[1];  // Flexible array member for the string data
};

void release_Tstring(struct TString* handle);
struct TStringHeap* precreate_Tstring_on_heap(uint32_t length);
struct TString* create_Tstring_on_heap(const char* value, uint32_t length);
void create_Tstring_on_stack(struct TString* header, const char* value,
                             uint32_t length);
struct TString* duplicate_Tstring(struct TString* handle);

//////////////////
// Public C API //
//////////////////

/// Returns the buffer of the string.
inline const char* tstr_buf(const struct TString* s) { return s->ptr; }

/// Returns the length of the string.
inline size_t tstr_len(const struct TString* s) { return s->length; }
