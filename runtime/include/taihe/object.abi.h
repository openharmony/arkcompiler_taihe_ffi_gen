/*
 * Copyright (c) 2025-2026 Huawei Device Co., Ltd.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef TAIHE_OBJECT_ABI_H
#define TAIHE_OBJECT_ABI_H

#include <taihe/common.h>

#include <stdint.h>
#include <stdlib.h>

// Storage modes are private duplication strategies. They do not determine an
// object handle's public ownership or drop responsibility.
enum TObjectStorageMode {
    TOBJ_STORAGE_STATIC = 0,
    TOBJ_STORAGE_SHAREABLE = 1,
    TOBJ_STORAGE_PROMOTABLE = 2,
};

struct DataBlockHead;

typedef void const *InterfaceId;

typedef size_t hash_func_t(struct DataBlockHead *);
typedef bool same_func_t(struct DataBlockHead *, struct DataBlockHead *);
typedef void const *qivp_func_t(struct DataBlockHead *, InterfaceId);
typedef void free_func_t(struct DataBlockHead *);
typedef struct DataBlockHead *promote_func_t(struct DataBlockHead *);

// Defines the operations associated with a data block's storage mode and type.
//
// # Members
// - `hash_fptr`: Computes the hash of a data block.
// - `same_fptr`: Compares equality of two data blocks.
// - `qivp_fptr`: Queries the vtable pointer for the specified interface ID.
// - `free_fptr`: Releases a shareable data block after its last holder is
//   dropped.
// - `promote_fptr`: Creates a holder from a promotable borrowed view.
struct TypeInfo {
    // Common operations for all storage modes.
    hash_func_t *hash_fptr;
    same_func_t *same_fptr;
    qivp_func_t *qivp_fptr;

    union {
        // Operations for shareable storage mode only.
        struct {
            free_func_t *free_fptr;
        };

        // Operations for promotable storage mode only.
        struct {
            promote_func_t *promote_fptr;
        };
    };
};

// Runtime metadata shared by object holders and borrowed views.
//
// # Members
// - `rtti_ptr`: A pointer to the runtime type information structure.
// - `flags`: The private storage mode of the data block.
// - `ref_count`: The holder reference count for shareable storage.
struct DataBlockHead {
    uint32_t mode;
    struct TypeInfo const *rtti_ptr;
    TRefCount ref_count;
};

// Initializes a static data block.
//
// # Arguments
// - `data_ptr`: Pointer to the data block.
// - `rtti_ptr`: Runtime type information.
//
// # Notes
// - Static data blocks have no holder reference count and are not managed by
//   the runtime.
TH_EXPORT void tobj_init_static(struct DataBlockHead *data_ptr, struct TypeInfo const *rtti_ptr);

// Initializes a shareable data block with one holder reference.
//
// # Arguments
// - `data_ptr`: Pointer to the data block.
// - `rtti_ptr`: Runtime type information whose free operation releases the
//   data block.
//
// # Notes
// - The initial holder must eventually be passed exactly once to tobj_drop.
TH_EXPORT void tobj_init_shareable(struct DataBlockHead *data_ptr, struct TypeInfo const *rtti_ptr);

// Initializes a data block that backs promotable borrowed views.
//
// # Arguments
// - `data_ptr`: Pointer to the data block.
// - `rtti_ptr`: Runtime type information whose promote operation creates a
//   holder from the data block.
//
// # Notes
// - This function creates no holder and no drop responsibility.
TH_EXPORT void tobj_init_promotable(struct DataBlockHead *data_ptr, struct TypeInfo const *rtti_ptr);

// Creates a holder from an object handle.
//
// # Arguments
// - `data_ptr`: Pointer from a holder or borrowed view. Null is valid.
//
// # Returns
// - An independent holder pointer, or null if `data_ptr` is null or invalid.
TH_EXPORT struct DataBlockHead *tobj_dup(struct DataBlockHead *data_ptr);

// Fulfills the drop responsibility of one holder.
//
// # Arguments
// - `data_ptr`: The holder pointer whose responsibility is consumed. Null is
//   valid.
//
// # Notes
// - This function consumes holders only. Borrowed views have no drop
//   responsibility and must not be passed to this function.
TH_EXPORT void tobj_drop(struct DataBlockHead *data_ptr);

#endif  // TAIHE_OBJECT_ABI_H
