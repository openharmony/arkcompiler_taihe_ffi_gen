import * as test from "../author_generated/opaque_test"

loadLibrary("ani_opaque")

class A {
    constructor() {}
}

function test_is_string_with_object() {
    const a = new A();
    const result = test.is_string(a);
    assertEQ(result, false)
}

function test_is_string_with_string() {
    const result = test.is_string("hello");
    assertEQ(result, true)
}

function test_is_string_with_undefined() {
    const result = test.is_string(undefined);
    assertEQ(result, false)
}

function test_get_object() {
    const object = test.get_object();
    assertEQ(object, "BBB")
}

function test_is_object_with_union() {
    const a = new test.Person("aaa");
    assertEQ(test.is_opaque(a), true);
    assertEQ(test.is_opaque("bbb"), false);
}

function test_get_objects() {
    const objects = test.get_objects();
    assertEQ(objects[0], "AAA")
    assertEQ(objects[1], undefined)
}

function main() {
    console.log("##############start#############");
    const suite = new ArkTestsuite("Test Suite");

    suite.addTest("test is_string with object", test_is_string_with_object);
    suite.addTest("test is_string with string", test_is_string_with_string);
    suite.addTest(
        "test is_string with undefined", test_is_string_with_undefined);
    suite.addTest("test is_string with union", test_is_object_with_union);
    suite.addTest("test get_object", test_get_object);
    suite.addTest("test get_objects", test_get_objects);

    suite.run();
}