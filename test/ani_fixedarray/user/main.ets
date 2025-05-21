import * as hello from "hello";

loadLibrary("ani_fixedarray");

function testFixedArrayBoolean(
    test: hello.TestInterface, booleanArray: hello.FixedArray<boolean>) {
    test.setFixedArrayBoolean(booleanArray);
    let result = test.getFixedArrayBoolean();
    assertEQ(booleanArray.length, result.length);
    for (let i = 0; i < booleanArray.length; i++) {
        assertEQ(booleanArray[i], result[i]);
    }
}

function testFixedArrayNumber(
    test: hello.TestInterface, numberArray: hello.FixedArray<number>) {
    test.setFixedArrayNumber(numberArray);
    let result = test.getFixedArrayNumber();
    assertEQ(numberArray.length, result.length);
    for (let i = 0; i < numberArray.length; i++) {
        assertEQ(numberArray[i], result[i]);
    }
}

function testFixedArrayString(
    test: hello.TestInterface, stringArray: hello.FixedArray<string>) {
    test.setFixedArrayString(stringArray);
    let result = test.getFixedArrayString();
    assertEQ(stringArray.length, result.length);
    for (let i = 0; i < stringArray.length; i++) {
        assertEQ(stringArray[i], result[i]);
    }
}

function testFixedArrayData(
    test: hello.TestInterface, dataArray: hello.FixedArray<hello.Data>) {
    test.setFixedArrayData(dataArray);
    let result = test.getFixedArrayData();
    assertEQ(dataArray.length, result.length);
}

function testOptionalFixedArrayData(
    test: hello.TestInterface,
    optionalDataArray: hello.FixedArray<hello.Data>|undefined) {
    test.setOptionalFixedArrayData(optionalDataArray);
    let result = test.getOptionalFixedArrayData();
    if (optionalDataArray === undefined) {
        assertEQ(result, undefined);
    } else {
        assertEQ(optionalDataArray.length, result?.length);
    }
}

function main() {
    const suite = new ArkTestsuite("FixedArray Test");

    let test = new hello.TestInterface();

    suite.addTest("FixedArrayBoolean", () => {
        testFixedArrayBoolean(test, [true, false, true]);
    });
    suite.addTest("FixedArrayNumber", () => {
        testFixedArrayNumber(test, [1.1, 2.2, 3.3]);
    });
    suite.addTest("FixedArrayString", () => {
        testFixedArrayString(test, ["hello", "world", "test"]);
    });
    suite.addTest("FixedArrayData", () => {
        testFixedArrayData(test, [{}, {}, {}]);
    });
    suite.addTest("OptionalFixedArrayData", () => {
        testOptionalFixedArrayData(test, [{}, {}, {}]);
    });
    suite.addTest("OptionalFixedArrayData", () => {
        testOptionalFixedArrayData(test, undefined);
    });

    exit(suite.run());
}
