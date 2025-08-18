import * as lib_a from "my_module_a";
import * as lib_b from "my_module_b";

function main() {
    let a = lib_a.ns1.Color.BLUE;
    console.log(lib_a.ns1.Funtest(a));
    let s: lib_a.ns1.ns2.ns3.ns4.ns5.MyStruct = {a: 1, b: 2};
    console.log(lib_a.ns1.ns2.ns3.ns4.ns5.Funtest(s));
    let iabse = lib_b.functiontest.makeIBase("aaaaa");
    console.log(iabse.getId());

    lib_a.baz();
    lib_a.ns1.noo();
    lib_a.ns1.ns2.ns3.ns4.ns5.foo();
    lib_b.functiontest.bar();
}
main();