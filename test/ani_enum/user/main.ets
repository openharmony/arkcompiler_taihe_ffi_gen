import * as EnumTest from "../author_generated/enum_test"

loadLibrary("ani_enum")

function main() {
    console.log("run main ... EnumTest ...")

    let color = EnumTest.Color.GREEN;
    EnumTest.showEnum(color);
    console.log(EnumTest.nextEnum(color))
}
