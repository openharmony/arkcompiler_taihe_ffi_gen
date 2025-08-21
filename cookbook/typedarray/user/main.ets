import {BusinessError} from "@ohos.base";
import * as typearr from "typedarray";

loadLibrary("typedarray");

function main() {
    // ets 侧创建，c++ 侧调用
    let arrbuf = new ArrayBuffer(8);
    arrbuf.set(0, (0xff).toByte());
    arrbuf.set(1, (0xff).toByte());
    arrbuf.set(2, (0x01).toByte());
    arrbuf.set(3, (0x00).toByte());
    let ets_uarr = new Uint16Array(arrbuf, 0, 2);
    typearr.printUint16Array(ets_uarr);

    // C++ 侧创建，ets 侧调用
    let c_uarr = typearr.createUint16Array();
    console.log(c_uarr);
}