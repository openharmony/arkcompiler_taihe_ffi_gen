import * as OverloadTest from "../author_generated/overload_test"

loadLibrary("ani_overload")

function test_add_numbers() {
    const result = OverloadTest.add(1, 2);
    assertEQ(result, 3);
}

function test_add_strings() {
    const result = OverloadTest.add("1", "2");
    assertEQ(result, "12");
}

function test_Foo_bar_number(foo: OverloadTest.Foo) {
    const result = foo.bar(123);
    assertEQ(result, 123);
}

function test_Foo_bar_string(foo: OverloadTest.Foo) {
    const result = foo.bar("Hello");
    assertEQ(result, "Hello");
}

function main() {
    console.log("##############start#############");
    const suite = new ArkTestsuite("Overload Test");

    suite.addTest("test add numbers", test_add_numbers);
    suite.addTest("test add strings", test_add_strings);
    
    let foo = OverloadTest.makeFoo();

    suite.addTest("test Foo bar with number", () => test_Foo_bar_number(foo));
    suite.addTest("test Foo bar with string", () => test_Foo_bar_string(foo));

    suite.run();
}
