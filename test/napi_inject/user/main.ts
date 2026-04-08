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
    if (lib_a.PI !== 3.14159) throw new Error(`Unexpected result`);

    // Test ts interface interface inject
    let baseimpl_a: BaseImpl = new BaseImpl("A");
    let res_baseimpl_a_add = baseimpl_a.add(2, 3);
    console.log("ts inject into interface interface:", res_baseimpl_a_add);
    if (res_baseimpl_a_add !== 5) throw new Error(`Unexpected result`);

    // Test ts interface class inject
    let ctest = new lib_a.ns1.CTest(100);
    let res_ctest_mul = ctest.mul(2, 3);
    console.log("ts inject into interface class:", res_ctest_mul);
    if (res_ctest_mul !== 6) throw new Error(`Unexpected result`);

    // Test ts struct interface inject
    let mystruct: MyStructImpl = new MyStructImpl(10, 20);
    let res_mystruct_add = mystruct.add(2, 3);
    console.log("ts inject into struct interface:", res_mystruct_add);
    if (res_mystruct_add !== 35) throw new Error(`Unexpected result`);

    // Test ts interface class inject
    let myclass = new lib_a.ns1.ns2.ns3.ns4.ns5.MyClass(true, 1.0);
    let res_ns5_myclass_add = lib_a.ns1.ns2.ns3.ns4.ns5.MyClass.add(1, 2);
    console.log("struct class:", myclass.a, myclass.b, res_ns5_myclass_add);
    let res_ns5_myclass_mul = myclass.mul(2, 3);
    console.log("ts inject into interface class:", res_ns5_myclass_mul);
    if (myclass.a !== true) throw new Error(`Unexpected result`);
    if (myclass.b !== 1) throw new Error(`Unexpected result`);
    if (res_ns5_myclass_add !== 3) throw new Error(`Unexpected result`);
    if (res_ns5_myclass_mul !== 6) throw new Error(`Unexpected result`);

    // Test dts inject (overload)
    let res_n_dts = lib_b.functiontest.concat(1);
    console.log("dts overload concat number:", res_n_dts);
    if (res_n_dts !== 11) throw new Error(`Unexpected result`);
    let res_s_dts = lib_b.functiontest.concat("1");
    console.log("dts overload concat string:", res_s_dts);
    if (res_s_dts !== "1_concat") throw new Error(`Unexpected result`);

    // Test dts inject into module
    console.log("inject into module dts:", lib_b.rate);
    if (lib_b.rate !== 0.618) throw new Error(`Unexpected result`);

    // Test ts inject constructor overload
    let res_ns5_mytest_sum = lib_a.ns1.ns2.ns3.ns4.ns5.MyTest.sum(1, 2);
    console.log("struct class static method:", res_ns5_mytest_sum);
    let new_mytest_num = new lib_a.ns1.ns2.ns3.ns4.ns5.MyTest(1);
    let new_mytest_arraynum = new lib_a.ns1.ns2.ns3.ns4.ns5.MyTest([1, 2]);
    console.log("ts inject overload number:", new_mytest_num.a);
    console.log("ts inject overload array number:", new_mytest_arraynum.a);
    if (res_ns5_mytest_sum !== 2) throw new Error(`Unexpected result`);
    if (new_mytest_num.a[0] !== 1) throw new Error(`Unexpected result`);
    if (new_mytest_arraynum.a[0] !== 1 || new_mytest_arraynum.a[1] !== 2) throw new Error(`Unexpected result`);

    // Test ts inject
    if (lib_a.ns1.ns2.ns3.ns4.ns5.PI !== 3.14159) throw new Error(`Unexpected result`);

    // Test simple enum in ts file
    let myenum = lib_a.ns1.ns2.ns3.ns4.ns5.MyEnum;
    if (myenum.A !== 0) throw new Error(`Unexpected result`);
    if (myenum.B !== 1) throw new Error(`Unexpected result`);
    if (myenum.C !== 2) throw new Error(`Unexpected result`);

    // Test simple const enum in ts file
    if (lib_a.ns1.ns2.ns3.ns4.ns5.FLAG_A !== 1) throw new Error(`Unexpected result`);
    if (lib_a.ns1.ns2.ns3.ns4.ns5.FLAG_B !== 3) throw new Error(`Unexpected result`);

    // Test simple interface in ts file
    let myibase = lib_a.ns1.makeIBase("myid");
    if (myibase.getId() !== "myid") throw new Error(`Unexpected result`);
    if (myibase.Name !== "default_name") throw new Error(`Unexpected result`);
    myibase.setId("newid");
    myibase.Name = "new_name";
    if (myibase.getId() !== "newid") throw new Error(`Unexpected result`);
    if (myibase.Name !== "new_name") throw new Error(`Unexpected result`);

    // Test simple class in ts file
    let myctest = new lib_a.ns1.CTest(50);
    if(myctest.Name !== "default_name") throw new Error(`Unexpected result`);
    myctest.Name = "test_name";
    if(myctest.Name !== "test_name") throw new Error(`Unexpected result`);

    // Test interface inherit in ts file
    let ifacec = new lib_a.ns1.IfaceC();
    ifacec.func1();
    ifacec.func2();
    ifacec.func3();

    // Test struct interface extend in ts file
    let structc = new lib_a.ns1.C();
    if (structc.a !== 1 || structc.b !== 2 || structc.c !== 3) throw new Error(`Unexpected result`);
}

main();
