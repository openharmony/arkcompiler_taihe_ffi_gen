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

const lib = requireNapi('./union_test.so', RequireBaseDir.SCRIPT_DIR);

function main() {
  let u1_res = lib.printUnion(1);
  if ( u1_res !== "number") throw new Error(`Unexpected result`);
  let u2_res = lib.printUnion("str");
  if ( u2_res !== "string") throw new Error(`Unexpected result`);
  let u3_res = lib.printUnion(true);
  if ( u3_res !== "boolean") throw new Error(`Unexpected result`);
  let numbers: number[] = [1, 2, 3, 4, 5];
  let u4_res = lib.printUnion(numbers);
  if ( u4_res !== "array") throw new Error(`Unexpected result`);
  let map = new Map<number, string>();
  map.set(0, "0");
  map.set(1, "1");
  map.set(2, "2");
  let u5_res = lib.printUnion(map);
  if ( u5_res !== "map") throw new Error(`Unexpected result`);
  let set = new Set<string>();
  set.add("a");
  set.add("b");
  set.add("c");
  let u6_res = lib.printUnion(set);
  if ( u6_res !== "set") throw new Error(`Unexpected result`);
  let u7_res = lib.printUnion(undefined);
  if ( u7_res !== "undefined") throw new Error(`Unexpected result`);
  let u8_res = lib.printUnion(null);
  if ( u8_res !== "null") throw new Error(`Unexpected result`);
  let arrayBuffer = new ArrayBuffer(8);
  let u9_res = lib.printUnion(arrayBuffer);
  if ( u9_res !== "arraybuffer") throw new Error(`Unexpected result`);
  let bigint = BigInt(12);
  let u10_res = lib.printUnion(bigint);
  if ( u10_res !== "bigint") throw new Error(`Unexpected result`);
  let int16array = new Int16Array([1, 2, 3]);
  let u11_res = lib.printUnion(int16array);
  if ( u11_res !== "int16array") throw new Error(`Unexpected result`);
  let int32array = new Int32Array([1, 2, 3]);
  let u12_res = lib.printUnion(int32array);
  if ( u12_res !== "int32array") throw new Error(`Unexpected result`);
  let foo = new lib.Foo(1, "foo");
  let u13_res = lib.printUnion(foo);
  if ( u13_res !== "foo") throw new Error(`Unexpected result`);
  let bar = new lib.Bar();
  let u14_res = lib.printUnion(bar);
  if ( u14_res !== "bar") throw new Error(`Unexpected result`);
  
  let m1 = lib.makeUnion("string");
  if ( typeof m1 !== "string") throw new Error(`Unexpected result`);
  let m2 = lib.makeUnion("number");
  if ( typeof m2 !== "number") throw new Error(`Unexpected result`);
  let m3 = lib.makeUnion("boolean");
  if ( typeof m3 !== "boolean") throw new Error(`Unexpected result`);
  let m4 = lib.makeUnion("array");
  if ( !(m4 instanceof Array)) throw new Error(`Unexpected result`);
  for (const value of m4) {
    console.log(value);
  }
  let m5 = lib.makeUnion("map");
  if ( !(m5 instanceof Map)) throw new Error(`Unexpected result`);
  for (const [key, value] of m5) {
    console.log(key, value);
  }
  let m6 = lib.makeUnion("set");
  if ( !(m6 instanceof Set)) throw new Error(`Unexpected result`);
  for (const value of m6) {
    console.log(value);
  }
  let m7 = lib.makeUnion("undefined");
  if ( m7 !== undefined) throw new Error(`Unexpected result`);
  let m8 = lib.makeUnion("null");
  if ( m8 !== null) throw new Error(`Unexpected result`);
  let m9 = lib.makeUnion("arraybuffer");
  if ( !(m9 instanceof ArrayBuffer)) throw new Error(`Unexpected result`);
  let m10 = lib.makeUnion("bigint");
  if ( typeof m10 !== "bigint") throw new Error(`Unexpected result`);
  let m11 = lib.makeUnion("int16array");
  if ( !(m11 instanceof Int16Array)) throw new Error(`Unexpected result`);
  let m12 = lib.makeUnion("int32array");
  if ( !(m12 instanceof Int32Array)) throw new Error(`Unexpected result`);
}

main();
