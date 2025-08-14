import {BusinessError} from "@ohos.base";
import * as test from "inject_test";
import * as moduleA from "moduleA";

loadLibrary("ani_inject");

function main() {
    let res1: String = moduleA.toplevelFunc("hello");
    console.log("toplevelFunc: " + res1);
    let res2: int = moduleA.foo.foo(100);
    console.log("foo.foo: " + res2);
    let foo = new test.Foo();
    foo.callWithThis();
    foo.callWithThis();
    let structObj: test.RGB = {
        color: "red",
        r: 255,
        g: 0,
        b: 0,
    };
    console.log(structObj.color + " " + structObj.r);
}
