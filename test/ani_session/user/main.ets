import * as lib from "../author_generated/session_test"
loadLibrary("ani_session")

function test_func_a(my_iface: lib.IfaceD) {
    const result = my_iface.func_a();
    assertEQ(result, "a");
}

function test_func_b(my_iface: lib.IfaceD) {
    const result = my_iface.func_b();
    assertEQ(result, "b");
}

function test_func_c(my_iface: lib.IfaceD) {
    const result = my_iface.func_c();
    assertEQ(result, "c");
}

function test_func_d(my_iface: lib.IfaceD) {
    const result = my_iface.func_d();
    assertEQ(my_iface.name, "IfaceD");
    my_iface.name = "new name";
    assertEQ(my_iface.name, "new name");
    assertEQ(result, "d");
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

    const suite = new ArkTestsuite("Interface Tests");
    const my_iface = lib.getIfaceD();

    suite.addTest("test func_a", () => {test_func_a(my_iface)});
    suite.addTest("test func_b", () => {test_func_b(my_iface)});
    suite.addTest("test func_c", () => {test_func_c(my_iface)});
    suite.addTest("test func_d", () => {test_func_d(my_iface)});

    suite.run();
}