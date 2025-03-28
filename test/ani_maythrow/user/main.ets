import {maythrow} from "../author_generated/maythrow";

loadLibrary("ani_maythrow");

function check_no_error() {
    let res = maythrow(1)
    assertEQ(res, 11)
}

function check_error() {
    try {
        let res = maythrow(0)
    } catch (e) {
        assertEQ(e.toString(), "Error: some error happen")
    }
}

function main() {
    console.log("##############start#############")
    const suite = new ArkTestsuite("throw error ut")

    suite.addTest("check no error", check_no_error)
    suite.addTest("check error", check_error)
    suite.run()
}
