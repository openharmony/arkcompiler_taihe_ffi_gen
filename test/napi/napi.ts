import { add, mul } from "./integer"
import { concat, to_i32, from_i32 } from "./string";

function main() {
  let result1 = mul(20, 2);
  console.log(result1);
  let result2 = add(20, 2);
  console.log(result2);
  let result3 = concat("test", "concat");
  console.log(result3)
  let result4 = to_i32("test");
  console.log(result4)
  let result5 = from_i32(20);
  console.log(result5)
}

main();