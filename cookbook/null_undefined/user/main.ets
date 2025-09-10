import {BusinessError} from "@ohos.base";
import {makeNullableValue} from "nullabletype";

loadLibrary("null_undefined");

function main() {
    let nvalue = makeNullableValue(0);
    console.log("null: " + nvalue);
    let svalue = makeNullableValue(1);
    console.log("string: " + svalue);
    let ivalue = makeNullableValue(2);
    console.log("int: " + ivalue);
    let uvalue = makeNullableValue(10);
    console.log("undefined: " + uvalue);
}