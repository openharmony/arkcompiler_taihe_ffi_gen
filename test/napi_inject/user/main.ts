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

function main() {
    // Test ts inject (overload)
    let res_n = lib_a.concat(1);
    console.log("ts overload concat number:", res_n);
    let res_s = lib_a.concat("1");
    console.log("ts overload concat string:", res_s);

    // Test ts inject into module
    console.log("ts inject into module:", lib_a.PI);

    // Test ts interface inject
    let baseimpl_a: BaseImpl = new BaseImpl("A");
    console.log("ts inject into interface:", baseimpl_a.add(2, 3));

    // Test ts class inject
    let ctest = new lib_a.ns1.CTest(100);
    console.log("ts inject into class:", ctest.mul(2, 3));

    // Test dts inject (overload)
    let res_n_dts = lib_b.functiontest.concat(1);
    console.log("dts overload concat number:", res_n_dts);
    let res_s_dts = lib_b.functiontest.concat("1");
    console.log("dts overload concat string:", res_s_dts);

    // Test dts inject into module
    console.log("inject into module dts:", lib_b.rate);
}

main();