import * as UnionTest from "../author_generated/union_ani"

loadLibrary("ani_union")

function test_printUnion_with_undefined() {
    let res = UnionTest.printUnion(undefined);
    assertEQ(res, "u")
}

function test_printUnion_with_string() {
    let res = UnionTest.printUnion("name");
    assertEQ(res, "s")
}

function test_printUnion_with_number() {
    let res = UnionTest.printUnion(123);
    assertEQ(res, "i")
}

function test_printUnion_with_pair() {
    let pair: UnionTest.Pair = {a: "a", b: "b"};
    let res = UnionTest.printUnion(pair);
    assertEQ(res, "p")
}

function test_makeUnion_string() {
    const result = UnionTest.makeUnion("s");
    assertEQ(result, "string");
}

function test_makeUnion_number() {
    const result = UnionTest.makeUnion("i");
    assertEQ(result, 123);
}

function test_makeUnion_pair() {
    const result = UnionTest.makeUnion("p");
    if (result instanceof UnionTest.Pair) {
        assertEQ(result.a, "a");
        assertEQ(result.b, "b");
    } else {
        throw new Error("Result type error");
    }
}

function test_makeUnion_undefined() {
    const result = UnionTest.makeUnion("u");
    assertEQ(result, undefined);
}

function main() {
    console.log("##############start#############");
    const suite = new ArkTestsuite("UnionTest Tests");

    suite.addTest(
        "test printUnion with undefined", test_printUnion_with_undefined);
    suite.addTest("test printUnion with string", test_printUnion_with_string);
    suite.addTest("test printUnion with number", test_printUnion_with_number);
    suite.addTest("test printUnion with pair", test_printUnion_with_pair);
    suite.addTest("test makeUnion string", test_makeUnion_string);
    suite.addTest("test makeUnion number", test_makeUnion_number);
    suite.addTest("test makeUnion pair", test_makeUnion_pair);
    suite.addTest("test makeUnion undefined", test_makeUnion_undefined);

    suite.run();
}
