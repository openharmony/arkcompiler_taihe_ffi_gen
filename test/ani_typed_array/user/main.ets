import * as bar from "@generated/bar";

loadLibrary("ani_typed_array");

function main() {
    let buf = new ArrayBuffer(8);
    buf.set(0, 0x01 as byte);
    buf.set(1, 0x23 as byte);
    buf.set(2, 0x45 as byte);
    buf.set(3, 0x67 as byte);
    buf.set(4, 0x89 as byte);
    buf.set(5, 0xab as byte);
    buf.set(6, 0xcd as byte);
    buf.set(7, 0xef as byte);
    let x = new Uint16Array(buf, 2, 2);
    bar.inUint16Array(x);

    let y = bar.outUint16Array();
    console.log(y);
    console.log(y.byteLength);
    console.log(y.byteOffset);
    console.log(y.buffer);
}
