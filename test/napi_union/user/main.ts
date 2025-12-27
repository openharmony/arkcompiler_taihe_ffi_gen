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

const lib = requireNapi('./union_test.so', RequireBaseDir.SCRIPT_DIR);

function main() {
  let u1_res = lib.printUnion(1);
  if ( u1_res !== "number") throw new Error(`Unexpected result`);
  let u2_res = lib.printUnion("str");
  if ( u2_res !== "s") throw new Error(`Unexpected result`);
  let u3_res = lib.printUnion(true);
  if ( u3_res !== "bool") throw new Error(`Unexpected result`);
  let numbers: number[] = [1, 2, 3, 4, 5];
  let u4_res = lib.printUnion(numbers);
  if ( u4_res !== "array") throw new Error(`Unexpected result`);
  let map = new Map<number, string>();
  map.set(0, "0");
  map.set(1, "1");
  map.set(2, "2");
  let u5_res = lib.printUnion(map);
  if ( u5_res !== "map") throw new Error(`Unexpected result`);
  let u6_res = lib.printUnion(undefined);
  if ( u6_res !== "undefined") throw new Error(`Unexpected result`);
  let u7_res = lib.printUnion(null);
  if ( u7_res !== "null") throw new Error(`Unexpected result`);
  
  let m1 = lib.makeUnion("s");
  if ( m1 !== "string") throw new Error(`Unexpected result`);
  let m2 = lib.makeUnion("number");
  if ( m2 !== 1.12345) throw new Error(`Unexpected result`);
  let m3 = lib.makeUnion("bool");
  if ( m3 !== false) throw new Error(`Unexpected result`);
  console.log(lib.makeUnion("array"));
  let m5 = lib.makeUnion("map");
  for (const [key, value] of m5) {
    console.log(key, value);
  }
  let m6 = lib.makeUnion("undefined");
  if ( m6 !== undefined) throw new Error(`Unexpected result`);
  let m7 = lib.makeUnion("null");
  if ( m7 !== null) throw new Error(`Unexpected result`);
}

main();
