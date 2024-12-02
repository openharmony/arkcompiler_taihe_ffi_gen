#pragma once

#include <stdlib.h>
#include <stdint.h>

#include "common.h"

struct DataBlockHead;

// IdMapItem
// Represents an ID mapping item containing an ID and a vtable pointer.
//
// # Members
// - `id`: A constant pointer representing the interface ID.
// - `vtbl_ptr`: A pointer to the virtual table associated with the ID.
struct IdMapItem {
  const void* id;
  void* vtbl_ptr;  
};

// TypeInfo
// Represents metadata information for a type, including version, length, and function pointers.
//
// # Members
// - `version`: A 64-bit unsigned integer representing the version of the type information.
// - `len`: Size of the type information in bytes.
// - `inside_func_len`: Size of inside functions.
// - `addref`: Function pointer to a addref function for `TObject`.
// - `release`: Function pointer to a release function for `TObject`.
// - `idmap`: A flexible array of `IdMapItem` structures for ID-to-vtable mapping.
struct TypeInfo {
  uint64_t version;
  uint64_t len;
  void (*free_data)(struct DataBlockHead*);
  struct IdMapItem idmap[];
};

// DataBlockHead
struct DataBlockHead {
  struct TypeInfo* rtti_ptr;
  TRefCount m_count;
};

// TObject
struct TObject {
  void* vtbl_ptr;
  struct DataBlockHead* data_ptr;
};

// Retrieves the corresponding vtable pointer based on the given id from TypeInfo.
// # Arguments
// - `rtti_ptr`: Pointer to the TypeInfo structure.
// - `id`: The identifier to look up.
//
// # Returns
// - Returns the corresponding vtable pointer if found; otherwise, returns NULL.
TH_EXPORT void* tobj_get_pvtbl(struct TypeInfo* rtti_ptr, const void* id);

// Converts the source object to the target object based on the provided id, looking up the corresponding vtable pointer.
// # Arguments
// - `src`: Source TObject.
// - `dst`: Pointer to an uninitialized target TObject.
// - `id`: Identifier used for lookup.
//
// # Returns
// - Returns 1 if conversion is successful; otherwise, returns 0.
TH_EXPORT int tobj_dynamic_cast(struct TObject src, struct TObject *dst, const void* id);

// Increments the reference count of the given TObject.
// # Arguments
// - `tobj`: The TObject whose reference count is to be incremented.
//
// # Returns
// - This function does not return a value. It modifies the reference count of the TObject.
TH_EXPORT void tobj_addref(struct TObject tobj);

// Decrements the reference count of the given TObject. If the reference count reaches zero, the object is destroyed.
// # Arguments
// - `tobj`: The TObject whose reference count is to be decremented.
//
// # Returns
// - This function does not return a value. It may result in the destruction of the TObject if the reference count reaches zero.
TH_EXPORT void tobj_release(struct TObject tobj);

// Allocates memory for a function table of a specified length.
//
// # Arguments
// - `func_len`: The number of function pointers in the table.
//
// # Returns
// - A pointer to the newly allocated function table, with space for `func_len` function pointers and an initial `size_t`
//   to store the table length. If the required memory exceeds UINT32_MAX or allocation fails, returns `NULL`.
TH_EXPORT void* alloc_ftable(size_t func_len);

// Creates a new function table, copying function pointers from two existing tables.
//
// # Arguments
// - `ftable_ptr`: Pointer to the primary function table to copy from.
// - `default_ftable_ptr`: Pointer to the default function table, used if `ftable_ptr` does not have a function at a given position.
//
// # Returns
// - A pointer to the newly created function table that contains pointers from `ftable_ptr` where available,
//   or from `default_ftable_ptr` otherwise. The function returns `NULL` if memory allocation fails.
TH_EXPORT void* create_new_ftable(void* ftable_ptr, void* default_ftable_ptr);
