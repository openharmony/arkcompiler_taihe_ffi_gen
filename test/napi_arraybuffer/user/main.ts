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

const lib = requireNapi('./arraybuffer_test.so', RequireBaseDir.SCRIPT_DIR);

function main() {
  const arrbuf1 = new ArrayBuffer(16);
  const uint8View = new Uint8Array(arrbuf1);
  uint8View[0] = 1;
  uint8View[1] = 2;
  let sumArrayu8 = lib.SumArrayU8(arrbuf1);
  if ( sumArrayu8 !== 3) throw new Error(`Unexpected result`);
  console.log("sumArrayu8 is " + sumArrayu8);

  let getArrayBuffer = lib.GetArrayBuffer(4)
  if ( getArrayBuffer.byteLength !== 4) throw new Error(`Unexpected result`);
  console.log("getArrayBuffer length: " + getArrayBuffer.byteLength);
  const view = new Uint8Array(getArrayBuffer);

  console.log("ArrayBuffer contents:");
  for (let i = 0; i < view.length; i++) {
      console.log(view[i]);
  }
}

main();
