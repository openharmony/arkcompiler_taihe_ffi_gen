import * as test from "@generated/inject_test";
import * as System from "std/core/System";

loadLibrary("ani_inject");

function main() {
    let foo = test.makeFoo();
    foo.with_this();
}
