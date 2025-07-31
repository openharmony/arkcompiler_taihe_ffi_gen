import {BusinessError} from "@ohos.base";
import * as new_overload from "new_overload";

loadLibrary("new_overload");

function main() {
    let a: int = 1
    let b: int = 2
    let numbers: int[] = [1, 2, 3, 4, 5];
    console.log("add_two: " + new_overload.add(a, b))
    console.log("add_arr: " + new_overload.add(numbers))
}