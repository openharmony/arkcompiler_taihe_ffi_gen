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

function toStingArray() {
    let nums: int[] = [35, 45, 55];
    let res = ArrayTest.toStingArray(nums)
    console.log("new array is " + res)
    assertEQ(res.length, nums.length)
    for (let i = 0; i < res.length; i++) {
        assertEQ(res[i], `${nums[i]}`)
    }
}

function makeIntArray() {
    let arr = ArrayTest.makeIntArray(5, 3)
    console.log("new array is " + arr)
    assertEQ(arr.length, 3)
    for (let i = 0; i < arr.length; i++) {
        assertEQ(arr[i], 5)
    }
}

function makeEnumArray() {
    let arr = ArrayTest.makeEnumArray(ArrayTest.Color.GREEN, 5)
    console.log("new array is " + arr)
    assertEQ(arr.length, 5)
    for (let i = 0; i < arr.length; i++) {
        assertEQ(arr[i], ArrayTest.Color.GREEN)
    }
}

function makeRecordArray() {
    let arr = ArrayTest.makeRecordArray("k", 128, 3)
    console.log("new array is " + arr)
    assertEQ(arr.length, 3)
    for (let i = 0; i < arr.length; i++) {
        assertEQ(arr[i]["k"], 128)
    }
}

function makeStructArray() {
    let arr = ArrayTest.makeStructArray("a", "b", 5, 3)
    console.log("new array is " + arr)
    assertEQ(arr.length, 3)
    for (let i = 0; i < arr.length; i++) {
        assertEQ(arr[i].a, "a")
        assertEQ(arr[i].b, "b")
        assertEQ(arr[i].c, 5)
    }
}

function main() {
    console.log("run main ... ArrayTest ...")

    const suite = new ArkTestsuite("ArrayTest")
    suite.addTest("sumArray", sumArray)
    suite.addTest("getArrayValue", getArrayValue)
    suite.addTest("toStingArray", toStingArray)
    suite.addTest("makeIntArray", makeIntArray)
    suite.addTest("makeEnumArray", makeEnumArray)
    suite.addTest("makeRecordArray", makeRecordArray)
    suite.addTest("makeStructArray", makeStructArray)
    suite.run()
}