import { add, mul, sub, from_rgb, to_rgb, make_RGB, make_Color, to_color, from_color, make_Theme, from_theme, to_theme, show, makeIBase, copyIBase } from "./integer"
import { concat, to_i32, from_i32 } from "./string";
import { RGB, Color, Theme } from "./rgb"

function main() {
  let result1 = mul(20, 2);
  console.log(result1);
  let result2 = add(20, 2);
  console.log(result2);
  let result3 = concat("test", "concat");
  console.log(result3);
  let result4 = to_i32("test");
  console.log(result4);
  let result5 = from_i32(20);
  console.log(result5);
  let result6 = sub(3.2, 2.3, true);
  console.log(result6);

  let result7 = to_rgb(16);
  console.log("to_rgb: ", result7);
  const rgb_c = make_RGB(1, 2, 3);
  console.log("make_RGB: ", rgb_c);
  const rgb = new RGB(10, 2, 3);
  console.log("new RGB: ", rgb);
  let result8 = from_rgb(rgb);
  console.log("from js RGB: ", result8);
  let result9 = from_rgb(rgb_c);
  console.log("from c RGB: ", result9) 

  let result10 = make_Color("blue");
  console.log("make_Color: ", result10);
  const color = new Color("blue", true, 3.14, rgb);
  console.log("new color: ", color);
  let result11 = from_color(color);
  console.log("from js color: ", result11);
  rgb.r = 12;
  let result12 = to_color("white", true, 3.12, rgb);
  console.log("to color: ", result12);

  let result16 = show();
  console.log("show: ", result16);

  let result17 = makeIBase("abc");
  console.log("makeIBase: ", result17.getId())
  result17.setId("xyz")
  console.log("setIBase: ", result17.getId())
  let result18 = makeIBase("test");
  copyIBase(result18, result17);
  console.log("copyIBase: ", result17.getId(), result18.getId());

  let result13 = make_Theme(color, result17);
  console.log("make_Theme: ", result13, result13.ibase.getId());
  const theme = new Theme(color);   // 不支持 js 实现 interface
  console.log("new theme: ", theme);
  let result14 = from_theme(result13);
  console.log("from js theme: ", result14);
  let result15 = to_theme(color, result17);
  console.log("to theme: ", result15, result15.ibase.getId());
}

main();
