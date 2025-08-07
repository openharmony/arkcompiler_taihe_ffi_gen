import * as lib from "opaque_test";

function main() {
    console.log("test opaque param", lib.is_string("test"));
    console.log("test opaque param", lib.is_string(2));

    console.log("test opaque return value", lib.get_object());

    let arr = lib.get_objects();
    console.log("test opaque return array value", arr[0], arr[1]);

    let p: lib.Person = {name: "Mary"};
    console.log("test opaque param union", lib.is_opaque(p));
    console.log("test opaque param union", lib.is_opaque("1"));
}

main();
