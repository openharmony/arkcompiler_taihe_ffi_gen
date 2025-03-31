import * as NewNS from "@generated/new_ns";
import * as NSTest from "@generated/ns_test";
import * as System from "std/core/System";

loadLibrary("namespace");

function check_struct() {
    let data: NSTest.baz.Data = {a: "abc", b: "efg", c: 3};
    let res_struct = NSTest.baz.concatStruct(data)
    assertEQ(res_struct, "abcefg3")

    let newStruct = NSTest.baz.makeStruct("aaa", "bbb", 1)
    assertEQ(newStruct.a, "aaa")
    assertEQ(newStruct.b, "bbb")
    assertEQ(newStruct.c, 1)
}

function check_ns_nest() {
    let res = NSTest.foo.bar.add(1, 2)
    assertEQ(res, 3)
}

function check_interface() {
    let win: NSTest.foo.window = NSTest.foo.get_interface(10);
    let res = win.getheight();
    assertEQ(res, 10)
    win.setheight(20);
    res = win.getheight();
    assertEQ(res, 20)
    NSTest.foo.check_interface(win)
}

function check_multi_ns() {
    let res = NewNS.myfunc1(1, 2)
    assertEQ(res, 3)
    res = NewNS.my_ns.myfunc2(2, 3)
    assertEQ(res, 5)
}


function main() {
    const suite = new ArkTestsuite("namespace ut")

    suite.addTest("check_struct", check_struct)
    suite.addTest("check_ns_nest", check_ns_nest)
    suite.addTest("check_interface", check_interface)
    suite.addTest("check_multi_ns", check_multi_ns)
    System.exit(suite.run())
}