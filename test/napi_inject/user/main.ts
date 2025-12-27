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

// const lib_a = requireNapi('./my_module_a.so', RequireBaseDir.SCRIPT_DIR);        // Use .d.ts
const lib_b = requireNapi('./my_module_b.so', RequireBaseDir.SCRIPT_DIR);        // Use .d.ts
import * as lib_a from "./my_module_a";       // Use .ts
// import * as lib_b from "./my_module_b";       // Use .ts

class BaseImpl implements lib_a.ns1.IBase {
  id: string;
  constructor(id: string) {
    this.id = id;
  }
  getId(): string {
    return this.id;
  }
  setId(id: string): void {
    this.id = id;
    return;
  }
  add(a: number, b: number): number {
    return a + b;
  }
}

class MyStructImpl implements lib_a.ns1.ns2.ns3.ns4.ns5.MyStruct {
  a: number;
  b: number;
  constructor(a: number, b: number) {
    this.a = a;
    this.b = b;
  }
  add(a: number, b: number): number {
    return a + b + this.a + this.b;
  }
}

function main() {
    // Test ts inject (overload)
    let res_n = lib_a.concat(1);
    if (res_n !== 11) throw new Error(`Unexpected result`);
    console.log("ts overload concat number:", res_n);
    let res_s = lib_a.concat("1");
    if (res_s !== "1_concat") throw new Error(`Unexpected result`);
    console.log("ts overload concat string:", res_s);

    // Test ts inject into module
    console.log("ts inject into module:", lib_a.PI);

    // Test ts interface interface inject
    let baseimpl_a: BaseImpl = new BaseImpl("A");
    console.log("ts inject into interface interface:", baseimpl_a.add(2, 3));

    // Test ts interface class inject
    let ctest = new lib_a.ns1.CTest(100);
    console.log("ts inject into interface class:", ctest.mul(2, 3));

    // Test ts struct interface inject
    let mystruct: MyStructImpl = new MyStructImpl(10, 20);
    console.log("ts inject into struct interface:", mystruct.add(2, 3));

    // Test ts interface class inject
    let myclass = new lib_a.ns1.ns2.ns3.ns4.ns5.MyClass(true, 1.0);
    console.log("struct class:", myclass.a, myclass.b, lib_a.ns1.ns2.ns3.ns4.ns5.MyClass.add(1, 2));
    console.log("ts inject into interface class:", myclass.mul(2, 3));

    // Test dts inject (overload)
    let res_n_dts = lib_b.functiontest.concat(1);
    console.log("dts overload concat number:", res_n_dts);
    let res_s_dts = lib_b.functiontest.concat("1");
    console.log("dts overload concat string:", res_s_dts);

    // Test dts inject into module
    console.log("inject into module dts:", lib_b.rate);

    // Test ts inject constructor overload
    console.log("struct class static method:", lib_a.ns1.ns2.ns3.ns4.ns5.MyTest.sum(1, 2));
    let new_mytest_num = new lib_a.ns1.ns2.ns3.ns4.ns5.MyTest(1);
    let new_mytest_arraynum = new lib_a.ns1.ns2.ns3.ns4.ns5.MyTest([1, 2]);
    console.log("ts inject overload number:", new_mytest_num.a);
    console.log("ts inject overload array number:", new_mytest_arraynum.a);
}

main();