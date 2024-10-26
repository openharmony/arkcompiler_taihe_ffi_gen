#pragma once

#include <stdlib.h>
#include <stdint.h>

#include "common.h"


// IdMapItem
// Represents an ID mapping item containing an ID and a vtable pointer.
//
// # Members
// - `id`: A constant pointer representing the interface ID.
// - `vtableptr`: A pointer to the virtual table associated with the ID.
struct idMapItem {
  const void* id;
  void* vtableptr;  
};

// TypeInfo
// Represents metadata information for a type, including version, length, and function pointers.
//
// # Members
// - `version`: A 64-bit unsigned integer representing the version of the type information.
// - `len`: Size of the type information in bytes.
// - `dup`: Function pointer to a duplication function for `TH_Object`.
// - `drop`: Function pointer to a deallocation function for `TH_Object`.
// - `idmap`: A flexible array of `idMapItem` structures for ID-to-vtable mapping.
struct TypeInfo {
  uint64_t version;
  size_t len;
  struct TH_Object (*dup)(struct TH_Object);
  void (*drop)(struct TH_Object);
  struct idMapItem idmap[0];
};

// DataBlockHead
struct DataBlockHead {
  struct TypeInfo* ti_ptr;
  TRefCount m_count;
};

// TH_Object
struct THObject {
  void* vtableptr;
  struct DataBlockHead* data_ptr;
};

// Retrieves the corresponding vtable pointer based on the given id from TypeInfo.
// # Arguments
// - `typeInfo_ptr`: Pointer to the TypeInfo structure.
// - `id`: The identifier to look up.
//
// # Returns
// - Returns the corresponding vtable pointer if found; otherwise, returns NULL.
TH_EXPORT inline void* GetVtptr(struct TypeInfo* typeInfo_ptr, const void* id);

// Converts the source object to the target object based on the provided id, looking up the corresponding vtable pointer.
// # Arguments
// - `src`: Source TH_Object.
// - `dst`: Pointer to an uninitialized target TH_Object.
// - `id`: Identifier used for lookup.
//
// # Returns
// - Returns 1 if conversion is successful; otherwise, returns 0.
TH_EXPORT int Convert(struct THObject src, struct THObject *dst, const void* id);