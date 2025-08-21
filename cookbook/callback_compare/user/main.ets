import {BusinessError} from "@ohos.base";
import {cbCompare} from "cb_compare";

loadLibrary("callback_compare");

function main() {
    let callback_1 = () => {
        console.log("Callback 1 executed");
        return "Callback 1 result";
    };
    let callback_2 = () => {
        console.log("Callback 2 executed");
        return "Callback 2 result";
    };
    console.log("same callback: " + cbCompare(callback_1, callback_1))
    console.log("different callback: " + cbCompare(callback_1, callback_2))
}