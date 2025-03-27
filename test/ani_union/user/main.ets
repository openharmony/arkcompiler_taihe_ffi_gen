import * as UnionTest from "../author_generated/union_ani"

loadLibrary("ani_union")

function test_printMyUnion_with_undefined() {
    let res = UnionTest.printMyUnion(undefined);
    assertEQ(res, "u")
}

function test_printMyUnion_with_string() {
    let res = UnionTest.printMyUnion("name");
    assertEQ(res, "s")
}

function test_printMyUnion_with_number() {
    let res = UnionTest.printMyUnion(123.456 as float);
    assertEQ(res, "f")
}

function test_printMyUnion_with_pair() {
    let pair: UnionTest.Pair = {a: "a", b: "b"};
    let res = UnionTest.printMyUnion(pair);
    assertEQ(res, "p")
}

function test_makeMyUnion_string() {
    const result = UnionTest.makeMyUnion("s");
    assertEQ(result, "string");
}

function test_makeMyUnion_number() {
    const result = UnionTest.makeMyUnion("f");
    assertEQ(result, 123);
}

function test_makeMyUnion_pair() {
    const result = UnionTest.makeMyUnion("p");
    if (result instanceof UnionTest.Pair) {
        assertEQ(result.a, "a");
        assertEQ(result.b, "b");
    } else {
        throw new Error("Result type error");
    }
}

function test_makeMyUnion_undefined() {
    const result = UnionTest.makeMyUnion("u");
    assertEQ(result, undefined);
}

function main() {
    console.log("##############start#############");
    const suite = new ArkTestsuite("UnionTest Tests");

    suite.addTest(
        "test printMyUnion with undefined", test_printMyUnion_with_undefined);
    suite.addTest(
        "test printMyUnion with string", test_printMyUnion_with_string);
    suite.addTest(
        "test printMyUnion with number", test_printMyUnion_with_number);
    suite.addTest("test printMyUnion with pair", test_printMyUnion_with_pair);
    suite.addTest("test makeMyUnion string", test_makeMyUnion_string);
    suite.addTest("test makeMyUnion number", test_makeMyUnion_number);
    suite.addTest("test makeMyUnion pair", test_makeMyUnion_pair);
    suite.addTest("test makeMyUnion undefined", test_makeMyUnion_undefined);

    suite.run();
}
