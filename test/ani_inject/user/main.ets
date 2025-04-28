import * as test from "@generated/inject_test";
import {BusinessError} from "@ohos.base";
import * as System from "std/core/System";

loadLibrary("ani_inject");

function main() {
    let foo = test.makeFoo();
    foo.with_this();
}
