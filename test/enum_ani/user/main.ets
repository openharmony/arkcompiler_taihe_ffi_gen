import * as EnumTest from "../author_generated/enum_ani"

function main() {
    console.log("run main ... EnumTest ...")

    let color = new EnumTest.Color(1, undefined);
    let sum = EnumTest.addEnum(color, 10)
    console.log("sum is " + sum)
    assertEQ(sum, 11)

    let res = EnumTest.getEnum(3)
    console.log("enum is " + res.tag)
    assertEQ(res.tag, 3)
}