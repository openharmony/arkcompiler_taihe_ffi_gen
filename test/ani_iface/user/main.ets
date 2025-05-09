import * as IfaceReadonlyTest from "@generated/iface_readonly_test";
import * as IfaceTest from "@generated/iface_test";
import {BusinessError} from "@ohos.base";

loadLibrary("ani_iface");

class SubFoo implements IfaceTest.Foo {
    bar(): void {}

    name: string = "";
}

interface Person {
    get name(): string;
}

class SubPerson implements Person {
    readonly name: string = "";
}

function getIfaceName() {
    let foo = IfaceTest.getFooIface();
    let name = foo.name;
    console.log("foo.name is " + name)
    assertEQ(name, "foo")
}

function getIfaceReadonlyName() {
    let noo = IfaceReadonlyTest.getNooIface();
    let nooName = noo.name;
    console.log("noo.name is " + nooName)
    assertEQ(nooName, "noo")
}

function setIfaceName() {
    let foo = IfaceTest.getFooIface();
    foo.name = "alice"
    let name = foo.name;
    console.log("foo.name is " + name)
    assertEQ(name, "alice")
}

function printFooName() {
    let foo = IfaceTest.getFooIface();
    foo.name = "bob"
    let name = IfaceTest.printFooName(foo)
    console.log("foo.name is " + name)
    assertEQ(name, "bob")
}

function printNooName() {
    let noo = IfaceReadonlyTest.getNooIface();
    let name = IfaceReadonlyTest.printNooName(noo)
    console.log("noo.name is " + name)
    assertEQ(name, "noo")
}

function setSubFooName() {
    let subFoo = new SubFoo()
    subFoo.name = "aaa"
    let name = subFoo.name
    console.log("subFoo.name is " + name)
    assertEQ(name, "aaa")
}

function main() {
    console.log("run main ... IfacePropTest ...")

    const suite = new ArkTestsuite("IfacePropTest")
    suite.addTest("getIfaceName", getIfaceName)
    suite.addTest("getIfaceReadonlyName", getIfaceReadonlyName)
    suite.addTest("setIfaceName", setIfaceName)
    suite.addTest("printFooName", printFooName)
    suite.addTest("printNooName", printNooName)
    suite.addTest("setSubFooName", setSubFooName)
    exit(suite.run())
}