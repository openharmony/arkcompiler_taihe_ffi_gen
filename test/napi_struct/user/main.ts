import { from_rgb, to_rgb, to_color, from_color, RGB, Color } from "../generated/struct_test";

function main() {
  let rgb: RGB = {r: 1, g: 2, b: 3};
  let my_rgb = to_rgb(16);
  console.log("i32 to ts rgb: ", my_rgb.r, my_rgb.g, my_rgb.b);
  let my_rgb_i32 = from_rgb(my_rgb);
  console.log("from ts RGB to i32: ", my_rgb_i32);

  let color_new = new Color("hello", true, 1.314, rgb);
  console.log("new color", color_new.name, color_new.flag, color_new.price, color_new.rgb.r);
  let my_color = to_color("white", true, 3.12, my_rgb);
  console.log("f64 to ts color: ", my_color.name, my_color.flag, my_color.price, my_color.rgb.r);
  let my_color_f64 = from_color(color_new);
  console.log("from ts color to f64: ", my_color_f64);
}

main();
