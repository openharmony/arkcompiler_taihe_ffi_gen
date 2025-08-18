import { concat, to_i32, from_i32, show, add } from "string_test";

function main() {
  let concat_str = concat("test", "concat");
  console.log("function concat: ", concat_str);

  let i32_from_str = to_i32("test");
  console.log("function to_i32: ", i32_from_str);
  
  let str_from_i32 = from_i32(20);
  console.log("function from_i32: ", str_from_i32);
  
  let str_show = show();
  console.log("function show: ", str_show);

  let add_show = add(2, 3);
  console.log("function add: ", add_show);
}

main();
