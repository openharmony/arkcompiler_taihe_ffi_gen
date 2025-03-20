import * as onoff_test from "../author_generated/onoff"

loadLibrary("ani_onoff")

function main() {
    let a = onoff_test.getIBase("hello", "world")
    a.off("set", "hey")
    a.off("setNew", "wow")
    // toplevel func on
    onoff_test.on("foo", 1)
    onoff_test.on("bar", 2)
    onoff_test.on("baz", "abc")
    onoff_test.on("qux", "abc", 3)
    // toplevel func off
    onoff_test.off("foo", 1)
    onoff_test.off("bar", 2)
    onoff_test.off("baz", "abc")
    onoff_test.off("qux", "abc", 3)
    // undefined
    // onoff_test.on("ABC", 3)
    // onoff_test.off("ABC", 3)
}