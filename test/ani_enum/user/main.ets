import * as EnumTest from "../author_generated/enum_test"

loadLibrary("ani_enum")

function test_nextEnum_with_color() {
    const color = EnumTest.Color.GREEN;
    const nextColor = EnumTest.nextEnum(color);
    assertEQ(nextColor, EnumTest.Color.BLUE)
}

function main() {
    console.log("##############start#############");
    const suite = new ArkTestsuite("EnumTest Tests");

    let color = EnumTest.Color.GREEN;
    EnumTest.showEnum(color);
    suite.addTest("test nextEnum with color", test_nextEnum_with_color);

    suite.run();
}
