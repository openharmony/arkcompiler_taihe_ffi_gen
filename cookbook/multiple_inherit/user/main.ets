import {BusinessError} from "@ohos.base";
import * as multiple_inherit from "multiple_inherit";

loadLibrary("multiple_inherit");

function main() {
    let Obj = multiple_inherit.createIRect("Red", "Square");
    console.log("Obj's Color is: " + Obj.getColor());
    console.log("Obj's Shape is: " + Obj.getShape());
    console.log("Obj's Message is: " + Obj.getMessage());
}