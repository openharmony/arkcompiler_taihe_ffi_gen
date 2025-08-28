// import * as lib_a from "my_module_a";       // Use .d.ts
import * as lib_b from "my_module_b";       // Use .d.ts
import * as lib_a from "../generated/proxy/my_module_a";       // Use .ts
// import * as lib_b from "../generated/proxy/my_module_b";       // Use .ts

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
    console.log("ts overload concat number:", res_n);
    let res_s = lib_a.concat("1");
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
}

main();