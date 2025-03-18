import * as test from "../author_generated/opaque_test"

loadLibrary("ani_opaque")

class A {
    constructor() {}
}

function main() {
    let a = new A();

    console.log(test.is_string(a));
    console.log(test.is_string("hello"));
    console.log(test.is_string(undefined));

    console.log(test.get_objects());
}