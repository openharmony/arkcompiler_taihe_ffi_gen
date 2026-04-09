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

#ifndef TAIHE_CALLBACK_ABI_H
#define TAIHE_CALLBACK_ABI_H

#include <taihe/object.abi.h>

struct TCallbackFTable {
    void (*invoke)();  // The actual signature is unknown at this level, and will be casted in C++ code.
};

struct TCallbackVTable {
    struct TCallbackFTable const *ftbl_ptr_0;
};

struct TCallback {
    struct TCallbackVTable const *vtbl_ptr;
    struct DataBlockHead *data_ptr;
};

#endif  // TAIHE_CALLBACK_ABI_H
