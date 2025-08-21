import {BusinessError} from "@ohos.base";
import * as javalike_overload from "javalike_overload";

loadLibrary("javalike_overload");

function main() {
    let a: int = 1
    let b: int = 2
    let numbers: int[] = [1, 2, 3, 4, 5];
    console.log("add_two: " + javalike_overload.add(a, b))
    console.log("add_arr: " + javalike_overload.add(numbers))
}