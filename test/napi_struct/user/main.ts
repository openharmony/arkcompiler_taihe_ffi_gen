import { from_rgb, to_rgb, to_color, from_color } from "../author_generated/struct_test";

function main() {
  let my_rgb = to_rgb(16);
  console.log("i32 to ts rgb: ", my_rgb);
  let my_rgb_i32 = from_rgb(my_rgb);
  console.log("from ts RGB to i32: ", my_rgb_i32);

  let my_color = to_color("white", true, 3.12, my_rgb);
  console.log("f64 to ts color: ", my_color);
  let my_color_f64 = from_color(my_color);
  console.log("from ts color to f64: ", my_color_f64);
}

main();
