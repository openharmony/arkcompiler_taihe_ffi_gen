import {getDataMaythrow, maythrow, noReturnMaythrow} from "@generated/maythrow";
import * as System from "std/core/System";

loadLibrary("ani_maythrow");

function check_no_error() {
    let res = maythrow(1)
    assertEQ(res, 11)
}

function check_error() {
    let errorMsg: string = "";
    try {
        let res = maythrow(0)
    } catch (e) {
        errorMsg = e.toString();
    }
    assertEQ(errorMsg, "Error: some error happen");
}

function check_error_when_return_complex_object() {
    let errorMsg: string = "";
    try {
        let res = getDataMaythrow()
        console.log(res)
    } catch (e) {
        errorMsg = e.toString();
    }
    assertEQ(errorMsg, "Error: error in getDataMaythrow");
}

function check_error_when_no_return() {
    let errorMsg: string = "";
    try {
        noReturnMaythrow()
    } catch (e) {
        errorMsg = e.toString();
    }
    assertEQ(errorMsg, "Error: error in noReturnMaythrow");
}

function main() {
    console.log("##############start#############")
    const suite = new ArkTestsuite("throw error ut")

    suite.addTest("check no error", check_no_error)
    suite.addTest("check error", check_error)
    suite.addTest(
        "check error when return complex object",
        check_error_when_return_complex_object)
    suite.addTest("check error when no return", check_error_when_no_return)
    System.exit(suite.run())
}
