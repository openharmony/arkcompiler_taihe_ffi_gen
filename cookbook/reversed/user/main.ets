import {BusinessError} from "@ohos.base";
import * as native_user from "native_user";
import * as user_impl from "user_impl";

loadLibrary("reversed");

function main() {
    let obj: user_impl.IfaceA = new user_impl.ClassA("Tom", 18);
    let objName: string = native_user.useIfaceA(obj);
    console.log("ETS return: " + objName);
}