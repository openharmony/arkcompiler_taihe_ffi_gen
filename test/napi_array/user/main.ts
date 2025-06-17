import * as lib from "../generated/array_test";

function main() {
let numbers: number[] = [1, 2, 3, 4, 5];
let sum = lib.sumArray(numbers, 100)
console.log("sum is " + sum)

let nums: number[] = [35, 45, 55];
let res_getArrayValue = lib.getArrayValue(nums, 2);
console.log("getArrayValue index 2 is " + res_getArrayValue);

let res_toStingArray = lib.toStingArray(nums);
console.log("toStingArray new array is " + res_toStingArray);

let arr_makeIntArray = lib.makeIntArray(5, 3);
console.log("makeIntArray new array is " + arr_makeIntArray);

let arr_makeEnumArray = lib.makeEnumArray(lib.Color.GREEN, 5);
console.log("makeEnumArray new array is " + arr_makeEnumArray);

let arr_changeEnumArray = lib.changeEnumArray(arr_makeEnumArray, lib.Color.BLUE);
console.log("changeEnumArray new array is " + arr_changeEnumArray);

let arr_makeStructArray = lib.makeStructArray("a", "b", 5, 3)
console.log("makeStructArray new array is ")
for (let i = 0; i < arr_makeStructArray.length; i++) {
  console.log(arr_makeStructArray[i].a, arr_makeStructArray[i].b, arr_makeStructArray[i].c);
}

let arr_changeStructArray = lib.changeStructArray(arr_makeStructArray, "aa", "bb", 3);
console.log("changeStructArray new array is ")
for (let i = 0; i < arr_changeStructArray.length; i++) {
  console.log(arr_changeStructArray[i].a, arr_changeStructArray[i].b, arr_changeStructArray[i].c);
}

let arr_makeStructArrayArray = lib.makeStructArrayArray("a", "b", 5, 2, 3);
console.log("makeStructArrayArray new array is ");
for (let i = 0; i < arr_makeStructArrayArray.length; i++) {
  for (let j = 0; j < arr_makeStructArrayArray[i].length; j++) {
    console.log(arr_makeStructArrayArray[i][j].a, arr_makeStructArrayArray[i][j].b, arr_makeStructArrayArray[i][j].c);
  }
}

let arr_makeIfaceArray = lib.makeIfaceArray("iface");
console.log("makeIfaceArray new array is ");
for (let i = 0; i < arr_makeIfaceArray.length; i++) {
  console.log(arr_makeIfaceArray[i].getId());
}

let arr_changeIfaceArray = lib.changeIfaceArray(arr_makeIfaceArray, "newiface");
console.log("changeIfaceArray new array is ");
for (let i = 0; i < arr_changeIfaceArray.length; i++) {
  console.log(arr_changeIfaceArray[i].getId());
}
}

main();
