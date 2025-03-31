#pragma once

#include <taihe/common.h>

#include <stdint.h>
#include <stdlib.h>

struct DataBlockHead;

// IdMapItem
// Represents an ID mapping item containing an ID and a vtable pointer.
//
// # Members
// - `id`: A constant pointer representing the interface ID.
// - `vtbl_ptr`: A pointer to the virtual table associated with the ID.
struct IdMapItem {
  void const* id;
  void const* vtbl_ptr;
};

// TypeInfo
// Represents metadata information for a type, including version, length, and
// function pointers.
//
// # Members
// - `version`: A 64-bit unsigned integer representing the version of the type
// information.
// - `len`: Size of the type information in bytes.
// - `pre_idmap_func_count`: Size of inside functions.
// - `addref`: Function pointer to a addref function for `TObject`.
// - `release`: Function pointer to a release function for `TObject`.
// - `idmap`: A flexible array of `IdMapItem` structures for ID-to-vtable
// mapping.
struct TypeInfo {
  uint64_t version;
  void (*free)(struct DataBlockHead*);
  uint64_t len;
  struct IdMapItem idmap[];
};

// DataBlockHead
struct DataBlockHead {
  struct TypeInfo const* rtti_ptr;
  TRefCount m_count;
};

// Initializes the TObject with the given runtime typeinfo.
//
// # Arguments
// - `data_ptr`: The data pointer.
// - `rtti_ptr`: The runtime typeinfo pointer.
TH_EXPORT void tobj_init(struct DataBlockHead* data_ptr,
                         struct TypeInfo const* rtti_ptr);

// Increments the reference count of the given TObject.
//
// # Arguments
// - `data_ptr`: The data pointer.
//
// # Returns
// - The new data pointer.
TH_EXPORT struct DataBlockHead* tobj_dup(struct DataBlockHead* data_ptr);

// Decrements the reference count of the given TObject. If the reference count
// reaches zero, the object is destroyed.
//
// # Arguments
// - `tobj`: The data pointer.
//
// # Returns
// - This function does not return a value. It may result in the destruction of
// the TObject if the reference count reaches zero.
TH_EXPORT void tobj_drop(struct DataBlockHead* data_ptr);
