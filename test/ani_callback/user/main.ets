import * as lib from "@generated/callbackTest";
import {BusinessError} from "@ohos.base";

loadLibrary("ani_callback");

function test_void_input_void_output() {
    lib.test_cb_v(() => {
        console.log("void input void output callback!");
    });
}

function test_int_input_void_output() {
    lib.test_cb_i((a) => {
        assertEQ(a, 1);
    });
}

function test_string_boolean_input() {
    lib.test_cb_s((a, b) => {
        if (b) {
            assertEQ(a, "hello");
        }
    });
}

function test_string_return_value() {
    let result = lib.test_cb_rs((a) => {
        return "my return value";
    });
    assertEQ(result, "my return value");
}

function test_struct_input() {
    lib.test_cb_struct((a) => {
        let data:
            lib.Data = {a: (a.a + "main"), b: (a.b + "main"), c: (a.c + 100)};
        assertEQ(data.a, "amain");
        assertEQ(data.b, "bmain");
        assertEQ(data.c, 101);
        return data;
    });
}

function main() {
    console.log("##############start#############");
    const suite = new ArkTestsuite("Callback Tests");

    suite.addTest("test void input void output", test_void_input_void_output);
    suite.addTest("test int input void output", test_int_input_void_output);
    suite.addTest("test string boolean input", test_string_boolean_input);
    suite.addTest("test string return value", test_string_return_value);
    suite.addTest("test struct input", test_struct_input);

    exit(suite.run());
}
