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

#include "arraybuffer.impl.hpp"

#include "stdexcept"
#include "taihe/array.hpp"
#include "taihe/runtime.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {
int32_t convert2Int(array_view<uint8_t> a) {
  int32_t num = 0;
  if (a.size() >= 4) {
    num = *(int32_t *)a.begin();
  } else {
    set_business_error(1, "ArrayBuffer len < 4");
  }
  return num;
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_convert2Int(convert2Int);
// NOLINTEND
