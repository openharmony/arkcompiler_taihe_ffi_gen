import {BusinessError} from "@ohos.base";
import * as lib from "callbackTest";

loadLibrary("ani_callback");

function test_void_input_void_output() {
    lib.testCbV(() => {
        console.log("void input void output callback!");
    });
}

function test_int_input_void_output() {
    lib.testCbI((a) => {
        arktest.assertEQ(a, 1);
    });
}

function test_string_boolean_input() {
    lib.testCbS((a, b) => {
        if (b) {
            arktest.assertEQ(a, "hello");
        }
    });
}

function test_string_return_value() {
    let result = lib.testCbRs((a) => {
        return "my return value";
    });
    arktest.assertEQ(result, "my return value");
}

function test_struct_input() {
    lib.testCbStruct((a) => {
        let data:
            lib.Data = {a: (a.a + "main"), b: (a.b + "main"), c: (a.c + 100)};
        arktest.assertEQ(data.a, "amain");
        arktest.assertEQ(data.b, "bmain");
        arktest.assertEQ(data.c, 101);
        return data;
    });
}

function test_int_string_return_value() {
    let instance: lib.MyInterface = lib.getInterface();
    let result = instance.testCbIntString((a, b) => {
        arktest.assertEQ(a, 10);
        arktest.assertEQ(b, 100);
    });
    arktest.assertEQ(result, "testCbIntString");
}

function test_int_bool_return_value() {
    let instance: lib.MyInterface = lib.getInterface();
    let result = instance.testCbIntBool((a, b) => {
        arktest.assertEQ(a, 100);
        arktest.assertEQ(b, 1000000000 as double);
    });
    arktest.assertEQ(result, true);
}

function test_int_enum_return_value() {
    let instance: lib.MyInterface = lib.getInterface();
    let result = instance.testCbEnum((a) => {
        arktest.assertEQ(a, 10);
    })
    arktest.assertEQ(result.toString(), "123");
}

function main() {
    console.log("##############start#############");
    const suite = new arktest.ArkTestsuite("Callback Tests");

    suite.addTest("test void input void output", test_void_input_void_output);
    suite.addTest("test int input void output", test_int_input_void_output);
    suite.addTest("test string boolean input", test_string_boolean_input);
    suite.addTest("test string return value", test_string_return_value);
    suite.addTest("test struct input", test_struct_input);

    suite.addTest("test int string return value", test_int_string_return_value);
    suite.addTest("test int bool return value", test_int_bool_return_value);
    suite.addTest("test int enum return value", test_int_enum_return_value);
    exit(suite.run());
}