/*
 * Copyright (c) 2025 Huawei Device Co., Ltd.
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

#include <taihe/object.abi.h>

void tobj_init_static(struct DataBlockHead *data_ptr, struct TypeInfo const *rtti_ptr)
{
    data_ptr->mode = TOBJ_STORAGE_STATIC;
    data_ptr->rtti_ptr = rtti_ptr;
    tref_init(&data_ptr->ref_count, 0);
}

void tobj_init_shareable(struct DataBlockHead *data_ptr, struct TypeInfo const *rtti_ptr)
{
    data_ptr->mode = TOBJ_STORAGE_SHAREABLE;
    data_ptr->rtti_ptr = rtti_ptr;
    tref_init(&data_ptr->ref_count, 1);
}

void tobj_init_promotable(struct DataBlockHead *data_ptr, struct TypeInfo const *rtti_ptr)
{
    data_ptr->mode = TOBJ_STORAGE_PROMOTABLE;
    data_ptr->rtti_ptr = rtti_ptr;
    tref_init(&data_ptr->ref_count, 0);
}

struct DataBlockHead *tobj_dup(struct DataBlockHead *data_ptr)
{
    if (!data_ptr) {
        return nullptr;
    }
    if (data_ptr->mode == TOBJ_STORAGE_PROMOTABLE) {
        return data_ptr->rtti_ptr->promote_fptr(data_ptr);
    }
    if (data_ptr->mode == TOBJ_STORAGE_SHAREABLE) {
        tref_inc(&data_ptr->ref_count);
    }
    return data_ptr;
}

void tobj_drop(struct DataBlockHead *data_ptr)
{
    if (!data_ptr) {
        return;
    }
    if (data_ptr->mode == TOBJ_STORAGE_SHAREABLE) {
        if (tref_dec(&data_ptr->ref_count)) {
            data_ptr->rtti_ptr->free_fptr(data_ptr);
        }
    }
}
