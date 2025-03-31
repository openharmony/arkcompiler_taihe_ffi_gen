import * as OptTest from "@generated/opt";
import * as System from "std/core/System";

loadLibrary("ani_optional");

function showOptionalInt() {
    OptTest.showOptionalInt(100 as int)
}

function showOptionalInt_1() {
    OptTest.showOptionalInt(undefined)
}

function makeOptionalInt() {
    let res = OptTest.makeOptionalInt(true)
    console.log(res)
    assertTrue(res != undefined);
}

function makeOptionalInt_1() {
    let res = OptTest.makeOptionalInt(false)
    console.log(res)
    assertTrue(res == undefined);
}

function makeOptionalArray() {
    let res = OptTest.makeOptionalArray(true, 5, 3)
    console.log(res)
    assertTrue(res != undefined);
}

function makeOptionalArray_1() {
    let res = OptTest.makeOptionalArray(false, 5, 3)
    console.log(res)
    assertTrue(res == undefined);
}

function sendReturnResult() {
    let result: OptTest.ReturnResult = {results: ["ab", "cd", "ef"]};
    let res = OptTest.sendReturnResult(result)
    console.log(res)
    assertTrue(res != undefined);
}

function sendReturnResult_1() {
    let result: OptTest.ReturnResult = {results: undefined};
    let res = OptTest.sendReturnResult(result)
    console.log(res)
    assertTrue(res == undefined);
}

function main() {
    console.log("run main ... OptTest ...")

    const suite = new ArkTestsuite("OptTest")
    suite.addTest("showOptionalInt", showOptionalInt)
    suite.addTest("showOptionalInt_1", showOptionalInt_1)
    suite.addTest("makeOptionalInt", makeOptionalInt)
    suite.addTest("makeOptionalInt_1", makeOptionalInt_1)
    suite.addTest("makeOptionalArray", makeOptionalArray)
    suite.addTest("makeOptionalArray_1", makeOptionalArray_1)
    suite.addTest("sendReturnResult", sendReturnResult)
    suite.addTest("sendReturnResult_1", sendReturnResult_1)
    System.exit(suite.run())
}