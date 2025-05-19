import * as arraybuffer from "arraybuffer";
import {BusinessError} from "@ohos.base";

loadLibrary("arraybuffer");
function main() {
    let numbersU8: byte[] = [1, 1, 0, 0, 0];
    let arrbuf1: ArrayBuffer = new ArrayBuffer(numbersU8.length);
    for (let i = 0; i < numbersU8.length; i++) {
        arrbuf1.set(i, numbersU8[i]);
    }
    let num1 = arraybuffer.convert2Int(arrbuf1);
    console.log("num1: " + num1);

    // let arrbuf2: ArrayBuffer = new ArrayBuffer(3);
    // for (let i = 0; i < 3; i++) {
    //     arrbuf2.set(i, numbersU8[i]);
    // }
    // let num2 = arraybuffer.convert2Int(arrbuf2);
    // console.log("num2: " + num2);
}
