#pragma once
#include <stddef.h>
#include <stdint.h>

#include "common.h"
// #include <wchar.h>

enum TStringFlags {
  TSTRING_SHARED = 1,
};

// HSTRING header structure
typedef struct {
  uint32_t flags;
  uint32_t length;
  char const* ptr;
} Tstring_header;

// Shared HSTRING header with reference counting
typedef struct {
  Tstring_header header;
  TRefCount count;
  char buffer[1];  // Flexible array member for the string data
} shared_Tstring_header;

void release_Tstring(Tstring_header* handle);
shared_Tstring_header* precreate_Tstring_on_heap(uint32_t length);
Tstring_header* create_Tstring_on_heap(const char* value, uint32_t length);
void create_Tstring_on_stack(Tstring_header* header, const char* value,
                             uint32_t length);
Tstring_header* duplicate_Tstring(Tstring_header* handle);

typedef struct {
  Tstring_header* handle;
} Tstring;

// Functions to manipulate Tstring
void Tstring_init(Tstring* str);
void Tstring_init_from_handle(Tstring* str, void* ptr);
void Tstring_init_from_char(Tstring* str, const char* value, uint32_t size);
void Tstring_init_from_string_view(Tstring* str, const char* value,
                                   size_t size);
void Tstring_clear(Tstring* str);
void Tstring_copy(Tstring* dest, const Tstring* src);
void Tstring_move(Tstring* dest, Tstring* src);
void Tstring_assign_from_string_view(Tstring* str, const char* value,
                                     size_t size);
void Tstring_assign_from_char(Tstring* str, const char* value);
void Tstring_assign_from_initializer_list(Tstring* str, const char* value,
                                          size_t size);
const char* Tstring_cstr(const Tstring* str);
size_t Tstring_size(const Tstring* str);
int Tstring_empty(const Tstring* str);

// ABI management functions
void* Tstring_get_abi(const Tstring* str);
void Tstring_put_abi(Tstring* str, void* value);
void Tstring_attach_abi(Tstring* str, void* value);
void* Tstring_detach_abi(Tstring* str);
void Tstring_copy_from_abi(Tstring* str, void* value);
void Tstring_copy_to_abi(const Tstring* str, void** value);
