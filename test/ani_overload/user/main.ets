import * as OverloadTest from "../author_generated/overload_test"

loadLibrary("ani_overload")

function main() {
    console.log(OverloadTest.add(1, 2));
    console.log(OverloadTest.add("1", "2"));

    let foo = OverloadTest.makeFoo();
    foo.bar(123);
    foo.bar("Hello");
}