import {getDataMaythrow, maythrow, noReturnBusinessError, noReturnMaythrow} from "@generated/maythrow";
import {BusinessError} from "@ohos.base";

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

function check_business_error() {
    let error_code: number = 0
    let errorMsg: string = "";
    try {
        noReturnBusinessError()
    } catch (e) {
        e = e as BusinessError
        error_code = e.code
        errorMsg = e.toString();
    }
    assertEQ(error_code, 5)
    assertEQ(errorMsg, "Error: error in noReturnBusinessError")
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
    suite.addTest("check business error", check_business_error)
    exit(suite.run())
}
