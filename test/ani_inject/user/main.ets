import * as test from "inject_test";
import {BusinessError} from "@ohos.base";

loadLibrary("ani_inject");

function main() {
    let foo = test.makeFoo();
    foo.with_this();
}
