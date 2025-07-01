import {BusinessError} from "@ohos.base";
import * as test from "inject_test";

loadLibrary("ani_inject");

function main() {
    let foo = new test.Foo();
    foo.callWithThis();
    foo.callWithThis();
}
