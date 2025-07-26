import * as lib from "../generated/typedarray_test";

function main() {
  let arr = lib.NewUint8Array(5, 10);
  console.log("NewUint8Array:", arr);
  let sum = lib.SumUint8Array(arr);
  console.log("SumUint8Array:", sum);
  let floatArr = lib.NewFloat32Array(5, 3.14);
  console.log("NewFloat32Array:", floatArr);
  let floatSum = lib.SumFloat32Array(floatArr);
  console.log("SumFloat32Array:", floatSum);
}

main();
