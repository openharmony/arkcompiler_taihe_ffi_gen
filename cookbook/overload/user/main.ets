import * as overload from "../author_generated/overload";

loadLibrary("overload");

function main() {
    let a: int = 1
    let b: int = 2
    let numbers: int[] = [1, 2, 3, 4, 5];
    console.log("add_two: " + overload.add(a, b))
    console.log("add_arr: " + overload.add(numbers))
}