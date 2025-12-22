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

#include "integer.arithmetic.impl.hpp"

int32_t ohos_int_add(int32_t a, int32_t b) {
  return a + b;
}

int32_t ohos_int_sub(int32_t a, int32_t b) {
  return a - b;
}

int32_t ohos_int_mul(int32_t a, int32_t b) {
  return a * b;
}

integer::arithmetic::DivModResult ohos_int_divmod(int32_t a, int32_t b) {
  return {
      .quo = a / b,
      .rem = a % b,
  };
}

// NOLINTBEGIN
TH_EXPORT_CPP_API_add_i32(ohos_int_add);
TH_EXPORT_CPP_API_sub_i32(ohos_int_sub);
TH_EXPORT_CPP_API_mul_i32(ohos_int_mul);
TH_EXPORT_CPP_API_divmod_i32(ohos_int_divmod);
// NOLINTEND
