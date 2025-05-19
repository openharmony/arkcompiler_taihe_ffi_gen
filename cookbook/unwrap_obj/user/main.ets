import * as wrap_interface from "wrap_interface";
import {BusinessError} from "@ohos.base";

loadLibrary("unwrap_obj");

function main() {
    let obj = wrap_interface.makeFoo();
    wrap_interface.useFoo(obj);
}