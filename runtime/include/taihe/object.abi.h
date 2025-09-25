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
  void const *id;
  void const *vtbl_ptr;
};

typedef void free_func_t(struct DataBlockHead *);
typedef size_t hash_func_t(struct DataBlockHead *);
typedef bool same_func_t(struct DataBlockHead *, struct DataBlockHead *);

// TypeInfo
// Represents metadata information for a type, including version, length, and
// function pointers.
//
// # Members
// - `free_fptr`: Pointer to function that frees the data block.
// - `hash_fptr`: Pointer to function that computes the hash of a data block.
// - `same_fptr`: Pointer to function that compares equality of two data blocks.
// - `len`: A 64-bit unsigned integer representing the length of idmap.
// - `idmap`: An array of IdMapItem structures representing the ID to vtable
//   mapping.
struct TypeInfo {
  free_func_t *free_fptr;
  hash_func_t *hash_fptr;
  same_func_t *same_fptr;
  uint64_t len;
  struct IdMapItem idmap[];
};

// DataBlockHead
// Represents the head of a data block, containing a pointer to the runtime
// type information structure and a reference count.
//
// # Members
// - `rtti_ptr`: A pointer to the runtime type information structure.
// - `m_count`: A reference count for the data block.
struct DataBlockHead {
  struct TypeInfo const *rtti_ptr;
  TRefCount m_count;
};

// Initializes the TObject with the given runtime typeinfo.
//
// # Arguments
// - `data_ptr`: The data pointer.
// - `rtti_ptr`: The runtime typeinfo pointer.
TH_EXPORT void tobj_init(struct DataBlockHead *data_ptr,
                         struct TypeInfo const *rtti_ptr);

// Increments the reference count of the given TObject.
//
// # Arguments
// - `data_ptr`: The data pointer.
//
// # Returns
// - The new data pointer.
TH_EXPORT struct DataBlockHead *tobj_dup(struct DataBlockHead *data_ptr);

// Decrements the reference count of the given TObject. If the reference count
// reaches zero, the object is destroyed.
//
// # Arguments
// - `tobj`: The data pointer.
TH_EXPORT void tobj_drop(struct DataBlockHead *data_ptr);
