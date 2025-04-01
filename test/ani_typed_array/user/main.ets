import * as bar from "@generated/bar";
import * as foo from "@generated/foo";

loadLibrary("ani_typed_array");

function main() {
    let ab = new ArrayBuffer(8);
    ab.set(0, 0x01 as byte);
    ab.set(1, 0x23 as byte);
    ab.set(2, 0x45 as byte);
    ab.set(3, 0x67 as byte);
    ab.set(4, 0x89 as byte);
    ab.set(5, 0xab as byte);
    ab.set(6, 0xcd as byte);
    ab.set(7, 0xef as byte);
    let ua = new Uint16Array(ab, 2, 2);

    foo.inArrayBuffer(ab);
    let x = foo.outArrayBuffer();
    console.log(x);

    bar.inUint16Array(ua);
    let y = bar.outUint16Array();
    console.log(y);
    console.log(y.byteLength);
    console.log(y.byteOffset);
    console.log(y.buffer);
}
