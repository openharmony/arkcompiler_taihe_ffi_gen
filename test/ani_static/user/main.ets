import {BusinessError} from "@ohos.base";
import * as lib from "staticTest";

loadLibrary("ani_static");

function test_sumSync() {
    const result = lib.IBase.sumSync(10, 20);
    assertEQ(result, 200);
}

function test_addSync() {
    const result = lib.IBase.addSync(10, 20);
    assertEQ(result, 30);
}

function test_new_class() {
    let test = new lib.IBase("hello");
    assertEQ(test.get(), "hello");
}

function test_new_class_with_two_args() {
    let test_1 = new lib.IBase("hello", "test");
    assertEQ(test_1.get(), "test");
}

function main() {
    console.log("##############start#############");
    const suite = new ArkTestsuite("IBase Tests");

    suite.addTest("test sumSync", test_sumSync);
    suite.addTest("test addSync", test_addSync);
    suite.addTest("test new class", test_new_class);
    suite.addTest("test new class with two args", test_new_class_with_two_args);

    exit(suite.run());
}
