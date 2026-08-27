/*
 * Copyright (c) 2026 Huawei Device Co., Ltd.
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

#ifndef TAIHE_SHARED_SET_ABI_H
#define TAIHE_SHARED_SET_ABI_H

#include <taihe/object.abi.h>

struct TSharedSetFTable {
    uint64_t version;

    struct {
        void (*getSize)();
        void (*getKeys)();
        void (*forEachKey)();
        void (*has)();
        void (*insert)();
        void (*checkedInsert)();
        void (*remove)();
        void (*checkedRemove)();
        void (*clear)();
    } methods;
};

struct TSharedSetVTable {
    struct TSharedSetFTable const *ftbl_ptr_0;
};

struct TSharedSet {
    struct TSharedSetVTable const *vtbl_ptr;
    struct DataBlockHead *data_ptr;
};

#endif  // TAIHE_SHARED_SET_ABI_H