import * as lib from "string_test";

function main() {
  let concat_str = lib.concat("test", "concat");
  console.log("function concat: ", concat_str);

  let i32_from_str = lib.to_i32("test");
  console.log("function to_i32: ", i32_from_str);
  
  let str_from_i32 = lib.from_i32(20);
  console.log("function from_i32: ", str_from_i32);
  
  let str_show = lib.show();
  console.log("function show: ", str_show);

  let add_show = lib.add(2, 3);
  console.log("function add: ", add_show);
}

main();
