import * as IfaceTest from "@generated/keep_name_test";
import {BusinessError} from "@ohos.base";

loadLibrary("ani_keep_name");

class SubFoo implements IfaceTest.Foo {
    Bar(): void {}

    name: string = "";
}

interface Person {
    get name(): string;
}

class SubPerson implements Person {
    readonly name: string = "";
}

function getIfaceName() {
    let foo = IfaceTest.GetFooIface();
    let name = foo.name;
    console.log("foo.name is " + name)
    assertEQ(name, "foo")
}

function setIfaceName() {
    let foo = IfaceTest.GetFooIface();
    foo.name = "alice"
    let name = foo.name;
    console.log("foo.name is " + name)
    assertEQ(name, "alice")
}

function printFooName() {
    let foo = IfaceTest.GetFooIface();
    foo.name = "bob"
    let name = IfaceTest.PrintFooName(foo)
    foo.Bar();
    console.log("foo.name is " + name)
    assertEQ(name, "bob")
}

function setSubFooName() {
    let subFoo = new SubFoo()
    subFoo.name = "aaa"
    let name = subFoo.name
    subFoo.Bar()
    console.log("subFoo.name is " + name)
    assertEQ(name, "aaa")
}

function ibase_on() {
    let a = IfaceTest.GetIBase("hello", "world")
    try {
        a.on("set", () => {
            console.log("void input void output callback!");
        })
    } catch (error) {
        console.error("main finsih test ERROR ", error)
    }
}

function ibase_off() {
    let a = IfaceTest.GetIBase("hello", "world")
    try {
        a.off("set", () => {
            console.log("void input void output callback!");
        })
    } catch (error) {
        console.error("main finsih test ERROR ", error)
    }
}

function main() {
    console.log("run main ... IfacePropTest ...")

    const suite = new ArkTestsuite("IfacePropTest")
    suite.addTest("ibase_on", ibase_on)
    suite.addTest("ibase_off", ibase_off)
    suite.addTest("getIfaceName", getIfaceName)
    suite.addTest("setIfaceName", setIfaceName)
    suite.addTest("printFooName", printFooName)
    suite.addTest("setSubFooName", setSubFooName)
    exit(suite.run())
}
