import * as test from "test";

loadLibrary("ani_compare");

function testCallbackManager() {
    let manager = new test.CallbackManager();

    let callback_1 = () => {
        console.log("Callback 1 executed");
        return "Callback 1 result";
    };
    let callback_2 = () => {
        console.log("Callback 2 executed");
        return "Callback 2 result";
    };
    let callback_3 = () => {
        console.log("Callback 3 executed");
        return "Callback 3 result";
    };

    let str_1 = callback_1();
    let str_2 = callback_2();
    let str_3 = callback_3();

    assertEQ(manager.addCallback(callback_1), true);
    assertEQ(manager.addCallback(callback_2), true);
    assertEQ(manager.addCallback(callback_1), false);

    let arr_a = manager.invokeCallbacks();
    assertEQ(arr_a.length, 2);
    assertEQ(arr_a[0], str_1);
    assertEQ(arr_a[1], str_2);

    assertEQ(manager.removeCallback(callback_1), true);
    assertEQ(manager.removeCallback(callback_3), false);

    let arr_b = manager.invokeCallbacks();
    assertEQ(arr_b.length, 1);
    assertEQ(arr_b[0], str_2);
}

function main() {
    let suite = new ArkTestsuite("CallbackManager Test Suite");

    suite.addTest("CallbackManager Test", testCallbackManager);

    exit(suite.run());
}
