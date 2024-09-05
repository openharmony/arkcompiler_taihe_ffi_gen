#include "c_Tstring.h"

#include <assert.h>
#include <stdlib.h>
#include <string.h>

#include "common.h"

inline struct TStringHeap* to_heap(struct TString* s) {
  if (s->flags & TSTRING_SHARED) return NULL;
  return (struct TStringHeap*)s;
}

void tstr_free(struct TString* s) {
  struct TStringHeap* sh = to_heap(s);
  if (sh && tref_dec(&sh->count)) free(sh);
}

static struct TStringHeap* allocate_header(uint32_t length) {
  // The last member of `TStringHeap` already accounts for the '\0' terminator.
  size_t bytes_required = sizeof(struct TStringHeap) + sizeof(char) * length;
  struct TStringHeap* sh = malloc(bytes_required);
  if (!sh) return NULL;

  sh->header.flags = 0;
  sh->header.length = length;
  sh->header.ptr = sh->buffer;
  tref_inc(&sh->count);
  sh->buffer[length] = '\0';
  return sh;
}

const struct TString* tstr_new(const char* buf TH_NONNULL, size_t len) {
  if (len > UINT32_MAX) return NULL;
  if (buf[len] != '\0') return NULL;

  struct TStringHeap* sh = allocate_header(len);
  if (sh) memcpy(sh->buffer, buf, sizeof(char) * len);
  return (struct TString*)sh;
}

// duplicate Tstring
struct TString* duplicate_Tstring(struct TString* s) {
  if (!s) return NULL;

  struct TStringHeap* sh = to_heap(s);
  if (sh) {
    tref_inc(&sh->count);
    return s;
  }

  return create_Tstring_on_heap(s->ptr, s->length);
}

typedef struct {
  struct TString* handle;
} Tstring;

// Tstring functions
// Init
void Tstring_init(Tstring* str) { str->handle = NULL; }

void Tstring_init_from_handle(Tstring* str, void* ptr) {
  str->handle = (struct TString*)ptr;
}

void Tstring_init_from_char(Tstring* str, const char* value, uint32_t size) {
  str->handle = create_Tstring_on_heap(value, size);
}

void Tstring_init_from_string_view(Tstring* str, const char* value,
                                   size_t size) {
  Tstring_init_from_char(str, value, (uint32_t)size);
}

// Clear
void Tstring_clear(Tstring* str) {
  if (str->handle) {
    release_Tstring(str->handle);
    str->handle = NULL;
  }
}

// Copy
void Tstring_copy(Tstring* dest, const Tstring* src) {
  Tstring_clear(dest);
  if (src->handle) {
    dest->handle = duplicate_Tstring(src->handle);
  }
}

// Move
void Tstring_move(Tstring* dest, Tstring* src) {
  Tstring_clear(dest);
  dest->handle = src->handle;
  src->handle = NULL;
}

void Tstring_assign_from_char(Tstring* str, const char* value) {
  Tstring_init_from_char(str, value, (uint32_t)strlen(value));
}

void Tstring_assign_from_string_view(Tstring* str, const char* value,
                                     size_t size) {
  Tstring_assign_from_char(str, value);
}

void Tstring_assign_from_initializer(Tstring* str, const char* value,
                                     size_t size) {
  Tstring_init_from_char(str, value, (uint32_t)size);
}

const char* Tstring_cstr(const Tstring* str) {
  if (str->handle) {
    return str->handle->ptr;
  } else {
    return "";
  }
}

size_t Tstring_size(const Tstring* str) {
  if (str->handle) {
    return str->handle->length;
  } else {
    return 0;
  }
}

int Tstring_empty(const Tstring* str) { return str->handle == NULL; }

// ABI functions
void* Tstring_get_abi(const Tstring* str) { return (void*)(str->handle); }

void Tstring_put_abi(Tstring* str, void* value) {
  Tstring_clear(str);
  str->handle = (struct TString*)value;
}

void Tstring_attach_abi(Tstring* str, void* value) {
  Tstring_clear(str);
  str->handle = (struct TString*)value;
}

void* Tstring_detach_abi(Tstring* str) {
  void* temp = (void*)(str->handle);
  str->handle = NULL;
}

void Tstring_copy_from_abi(Tstring* str, void* value) {
  Tstring_attach_abi(str, duplicate_Tstring((struct TString*)value));
}

void Tstring_copy_to_abi(const Tstring* str, void** value) {
  if (*value == NULL) {
    *value = duplicate_Tstring(str->handle);
  }
}

// init copy release len ptr
