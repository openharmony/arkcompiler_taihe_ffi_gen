import {BusinessError} from "@ohos.base";
import * as rename_example from "rename_example";

loadLibrary("rename_example");

function main() {
    let res = rename_example.newFoo(1, 2);
    console.log("res = " + res);
}