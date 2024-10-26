#pragma once

#include <stdlib.h>
#include <stdint.h>

#include "common.h"


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
// - `dup`: Function pointer to a duplication function for `TObject`.
// - `drop`: Function pointer to a deallocation function for `TObject`.
// - `idmap`: A flexible array of `IdMapItem` structures for ID-to-vtable mapping.
struct TypeInfo {
  uint64_t version;
  size_t len;
  struct TObject (*dup)(struct TObject);
  void (*drop)(struct TObject);
  struct IdMapItem idmap[0];
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
