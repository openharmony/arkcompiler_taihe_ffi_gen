import * as ArrayTest from "../author_generated/array_test"

loadLibrary("ani_array")

function sumArray() {
    let numbers: int[] = [1, 2, 3, 4, 5];
    let sum = ArrayTest.sumArray(numbers, 100)
    console.log("sum is " + sum)
    assertEQ(sum, 115)
}

function getArrayValue() {
    let nums: long[] = [35, 45, 55];
    let res = ArrayTest.getArrayValue(nums, 2)
    console.log("index 2 is " + res)
    assertEQ(res, 55)
}

function makeIntArray() {
    let arr = ArrayTest.makeArray(5, 3)
    console.log("new array is " + arr)
    assertEQ(arr.length, 3)
    for (let i = 0; i < arr.length; i++) {
        assertEQ(arr[i], 5)
    }
}

function main() {
    console.log("run main ... ArrayTest ...")

    const suite = new ArkTestsuite("ArrayTest")
    suite.addTest("sumArray", sumArray)
    suite.addTest("getArrayValue", getArrayValue)
    suite.addTest("makeIntArray", makeIntArray)
    suite.run()
}