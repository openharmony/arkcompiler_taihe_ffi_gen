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

import * as lib from "typedarray_test";

function main() {
  let arr = lib.NewUint8Array(5, 10);
  if ( arr[0] !== 10) throw new Error(`Unexpected result`);
  console.log("NewUint8Array:", arr);
  let sum = lib.SumUint8Array(arr);
  if ( sum !== 50) throw new Error(`Unexpected result`);
  console.log("SumUint8Array:", sum);
  let floatArr = lib.NewFloat32Array(5, 3.14);
  console.log("NewFloat32Array:", floatArr);
  let floatSum = lib.SumFloat32Array(floatArr);
  console.log("SumFloat32Array:", floatSum);
}

main();
