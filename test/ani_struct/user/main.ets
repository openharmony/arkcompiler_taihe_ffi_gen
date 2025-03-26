import * as StructTest from "../author_generated/struct_test"

loadLibrary("ani_struct")

function main() {
    console.log("run main ... StructTest ...")

    let data: StructTest.Data = {a: "abc", b: "efg", c: 3};
    let res = StructTest.concatStruct(data)
    console.log("result is " + res)
    assertEQ(res, "abcefg3")

    let newStruct = StructTest.makeStruct("aaa", "bbb", 1)
    console.log(
        "new struct is " + newStruct.a + " " + newStruct.b + " " + newStruct.c)
    assertEQ(newStruct.a, "aaa")
    assertEQ(newStruct.b, "bbb")
    assertEQ(newStruct.c, 1)
}