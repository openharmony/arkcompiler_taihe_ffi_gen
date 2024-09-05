#include "c_Tstring.h"

#include <assert.h>
#include <stdlib.h>
#include <string.h>

#include "common.h"

// Release the Tstring
void release_Tstring(Tstring_header* handle) {
  if ((handle->flags & TSTRING_SHARED) == 0) {
    if (tref_dec(&(((shared_Tstring_header*)handle)->count))) {
      free(handle);
    }
  }
}

// allocation function
shared_Tstring_header* precreate_Tstring_on_heap(uint32_t length) {
  size_t bytes_required = sizeof(shared_Tstring_header) + sizeof(char) * length;

  shared_Tstring_header* header =
      (shared_Tstring_header*)malloc(bytes_required);
  if (!header) {
    // Memory allocation failure
    return NULL;
  }

  header->header.flags = 0;
  header->header.length = length;
  header->header.ptr = header->buffer;
  tref_inc(&(header->count));
  header->buffer[length] = '\0';
  return header;
}

// create Tstring_header on heap
Tstring_header* create_Tstring_on_heap(const char* value, uint32_t length) {
  if (length == 0) {
    return NULL;
  }

  shared_Tstring_header* header = precreate_Tstring_on_heap(length);
  if (header) {
    memcpy(header->buffer, value, sizeof(char) * length);
  }
  return (Tstring_header*)header;
}

// stack
void create_Tstring_on_stack(Tstring_header* header, const char* value,
                             uint32_t length) {
  assert(value);
  assert(length != 0);
  assert(value[length] == '\0');

  header->flags = 1;
  header->length = length;
  header->ptr = value;
}

// duplicate Tstring
Tstring_header* duplicate_Tstring(Tstring_header* handle) {
  if (!handle) {
    return NULL;
  } else if ((handle->flags & TSTRING_SHARED) == 0) {
    tref_inc(&(((shared_Tstring_header*)handle)->count));
    return handle;
  } else {
    return create_Tstring_on_heap(handle->ptr, handle->length);
  }
}

// Tstring functions
// Init
void Tstring_init(Tstring* str) { str->handle = NULL; }

void Tstring_init_from_handle(Tstring* str, void* ptr) {
  str->handle = (Tstring_header*)ptr;
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

void Tstring_assign_from_string_view(Tstring* str, const char* value,
                                     size_t size) {
  Tstring_assign_from_char(str, value);
}

void Tstring_assign_from_char(Tstring* str, const char* value) {
  Tstring_init_from_char(str, value, (uint32_t)strlen(value));
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
  str->handle = (Tstring_header*)value;
}

void Tstring_attach_abi(Tstring* str, void* value) {
  Tstring_clear(str);
  str->handle = (Tstring_header*)value;
}

void* Tstring_detach_abi(Tstring* str) {
  void* temp = (void*)(str->handle);
  str->handle = NULL;
}

void Tstring_copy_from_abi(Tstring* str, void* value) {
  Tstring_attach_abi(str, duplicate_Tstring((Tstring_header*)value));
}

void Tstring_copy_to_abi(const Tstring* str, void** value) {
  if (*value == NULL) {
    *value = duplicate_Tstring(str->handle);
  }
}

// init copy release len ptr
