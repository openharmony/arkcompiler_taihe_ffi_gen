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

    arktest.assertEQ(manager.addCallback(callback_1), true);
    arktest.assertEQ(manager.addCallback(callback_2), true);
    arktest.assertEQ(manager.addCallback(callback_1), false);

    let arr_a = manager.invokeCallbacks();
    arktest.assertEQ(arr_a.length, 2);
    arktest.assertEQ(arr_a[0], str_1);
    arktest.assertEQ(arr_a[1], str_2);

    arktest.assertEQ(manager.removeCallback(callback_1), true);
    arktest.assertEQ(manager.removeCallback(callback_3), false);

    let arr_b = manager.invokeCallbacks();
    arktest.assertEQ(arr_b.length, 1);
    arktest.assertEQ(arr_b[0], str_2);
}

function main() {
    let suite = new arktest.ArkTestsuite("CallbackManager Test Suite");

    suite.addTest("CallbackManager Test", testCallbackManager);

    exit(suite.run());
}
