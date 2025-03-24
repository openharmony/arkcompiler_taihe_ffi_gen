import * as test from "../author_generated/inject_test"

loadLibrary("ani_inject")

function main() {
    let foo = test.makeFoo();
    foo.with_this();
}
