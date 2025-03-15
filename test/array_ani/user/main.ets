import * as ArrayTest from "../author_generated/array_ani"

function main() {
    console.log("run main ... ArrayTest ...")

    let numbers: int[] = [1, 2, 3, 4, 5];
    let sum = ArrayTest.sumArray(numbers, 100)
    console.log("sum is " + sum)
    assertEQ(sum, 115)

    let nums: int[] = [35, 45, 55];
    let res = ArrayTest.getArrayValue(nums, 2)
    console.log("index 2 is " + res)
    assertEQ(res, 55)

    let arr = ArrayTest.makeArray(5, 3)
    console.log("new array is " + arr)
    assertEQ(arr.length, 3)
    for (let i = 0; i < arr.length; i++) {
        assertEQ(arr[i], 5)
    }
}