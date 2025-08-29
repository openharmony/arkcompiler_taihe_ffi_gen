import {BusinessError} from "@ohos.base";
import * as lib from "staticTest";

loadLibrary("ani_static");

function test_sumSync() {
    const result = lib.IBase.sumSync(10, 20);
    console.log("sumSync result:", result);
    arktest.assertEQ(result, 200);
}

function test_addSync() {
    const result = lib.IBase.addSync(10, 20);
    arktest.assertEQ(result, 30);
}

function test_new_class() {
    let test = new lib.IBase("hello");
    console.log("new IBase get:", test.get());
    arktest.assertEQ(test.get(), "hello");
}

// Frontend javalike constructor overloading bug
// function test_new_class_with_two_args() {
//     let test_1 = new lib.IBase("hello", "test");
//     arktest.assertEQ(test_1.get(), "test");
// }

function main() {
    console.log("##############start#############");
    const suite = new arktest.ArkTestsuite("IBase Tests");

    suite.addTest("test sumSync", test_sumSync);
    suite.addTest("test addSync", test_addSync);
    suite.addTest("test new class", test_new_class);
    // Frontend javalike constructor overloading bug
    // suite.addTest("test new class with two args",
    // test_new_class_with_two_args);

    exit(suite.run());
}
