import {BusinessError} from "@ohos.base";
import * as deprecated_overload from "deprecated_overload";

loadLibrary("deprecated_overload");

function main() {
    let a: int = 1
    let b: int = 2
    let numbers: int[] = [1, 2, 3, 4, 5];
    console.log("add_two: " + deprecated_overload.add(a, b))
    console.log("add_arr: " + deprecated_overload.add(numbers))
}