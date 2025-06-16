import * as lib from "../generated/arraybuffer_test";

function main() {
  const arrbuf1 = new ArrayBuffer(16);
  const uint8View = new Uint8Array(arrbuf1);
  uint8View[0] = 1;
  uint8View[1] = 2;
  let sumArrayu8 = lib.SumArrayU8(arrbuf1)
  console.log("sumArrayu8 is " + sumArrayu8)

  let getArrayBuffer = lib.GetArrayBuffer(4)
  console.log("getArrayBuffer length: " + getArrayBuffer.byteLength);
  const view = new Uint8Array(getArrayBuffer);

  console.log("ArrayBuffer contents:");
  for (let i = 0; i < view.length; i++) {
      console.log(view[i]);
  }
}

main();
