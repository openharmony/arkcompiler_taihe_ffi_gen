import * as hello_world from "../author_generated/hello_world"
loadLibrary("hello_world")
function main() {
    let numA: Int = 1
    console.log("numA is : " + numA)
    let numB: Int = 2
    console.log("numB is : " + numB)
    let sum = hello_world.add(numA, numB)
    console.log("sum is : " + sum)
}