import * as inject from "../author_generated/inject"

loadLibrary("inject")

function main() {
    let foo = inject.makeFoo();
    foo.with_this();
    foo.with_name("my name");
    console.log("set foo.name = foo_new_name")
}