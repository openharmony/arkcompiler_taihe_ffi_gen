import * as lib from "../generated/union_test";

function main() {
  console.log(lib.printUnion(1));
  console.log(lib.printUnion("str"));
  console.log(lib.printUnion(true));
  let numbers: number[] = [1, 2, 3, 4, 5];
  console.log(lib.printUnion(numbers));
  let map = new Map<number, string>();
  map.set(0, "0");
  map.set(1, "1");
  map.set(2, "2");
  console.log(lib.printUnion(map));
  
  console.log(lib.makeUnion("s"));
  console.log(lib.makeUnion("number"));
  console.log(lib.makeUnion("bool"));
  console.log(lib.makeUnion("array"));
  console.log(lib.makeUnion("map"));
}

main();
