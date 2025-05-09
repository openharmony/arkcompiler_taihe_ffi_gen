import * as hello_ani from "@generated/hello_ani";
import {BusinessError} from "@ohos.base";
loadLibrary("hello_ani");

function main() {
    console.log("hello hello_ani main")
    console.log(hello_ani.add(1, 2))
}