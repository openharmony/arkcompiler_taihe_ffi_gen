import {BusinessError} from "@ohos.base";
import * as lib from "session_test";

loadLibrary("ani_session");

function test_func_a(my_iface: lib.IfaceD) {
    const result = my_iface.func_a();
    arktest.assertEQ(result, "a");
}

function test_func_b(my_iface: lib.IfaceD) {
    const result = my_iface.func_b();
    arktest.assertEQ(result, "b");
}

function test_func_c(my_iface: lib.IfaceD) {
    const result = my_iface.func_c();
    arktest.assertEQ(result, "c");
}

function test_func_d(my_iface: lib.IfaceD) {
    const result = my_iface.func_d();
    arktest.assertEQ(my_iface.name, "IfaceD");
    my_iface.name = "new name";
    arktest.assertEQ(my_iface.name, "new name");
    arktest.assertEQ(result, "d");
    try {
        my_iface.on("set", () => {
            console.log("void input void output callback!");
        })
    } catch (error) {
        console.error("main finsih test ERROR ", error)
    }
    try {
        my_iface.off("set", () => {
            console.log("void input void output callback!");
        })
    } catch (error) {
        console.error("main finsih test ERROR ", error)
    }
}

function test_func_e(my_iface: lib.IfaceE) {
    let result = my_iface.func_a();
    arktest.assertEQ(result, "aa");
    result = my_iface.func_b();
    arktest.assertEQ(result, "bb");
    result = my_iface.func_c();
    arktest.assertEQ(result, "cc");
    result = my_iface.func_e();
    arktest.assertEQ(result, "ee");
}

function main() {
    console.log("##############start#############");
    let ps = lib.getSession(1);
    if (ps instanceof lib.PhotoSession) {
        ps.beginConfig();
        ps.canPreconfig();
    }

    let vs = lib.getSession(0);
    if (vs instanceof lib.VideoSession) {
        vs.beginConfig();
        vs.canPreconfig();
    }

    const suite = new arktest.ArkTestsuite("Interface Tests");
    const my_iface = lib.getIfaceD();
    const my_iface_e = lib.getIfaceE();

    suite.addTest("test func_a", () => {test_func_a(my_iface)});
    suite.addTest("test func_b", () => {test_func_b(my_iface)});
    suite.addTest("test func_c", () => {test_func_c(my_iface)});
    suite.addTest("test func_d", () => {test_func_d(my_iface)});
    suite.addTest("test func_e", () => {test_func_e(my_iface_e)});

    exit(suite.run());
}
