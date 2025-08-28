import * as lib from "struct_test";

// Test error param type
function testDynamicInput(value: any) {
  try {
    let rgb = lib.to_rgb(value);
    console.log("result: ", rgb);
  } catch (e) {
    console.log("capture error message: ", e.message);
  }
}

function main() {
  let rgb: lib.RGB = {r: 1, g: 2, b: 3};
  let my_rgb = lib.to_rgb(16);
  console.log("i32 to ts rgb: ", my_rgb.r, my_rgb.g, my_rgb.b);
  let my_rgb_i32 = lib.from_rgb(my_rgb);
  console.log("from ts RGB to i32: ", my_rgb_i32);

  let my_color = lib.to_color("white", true, 3.12, my_rgb);
  console.log("f64 to ts color: ", my_color.name, my_color.flag, my_color.price, my_color.rgb.r);
  let my_color_f64 = lib.from_color(my_color);
  console.log("from ts color to f64: ", my_color_f64);

  let student: lib.Student = {name: "Jack", age: 10};
  let pro_student = lib.process_student(student);
  console.log("process student: ", pro_student.name, pro_student.age)
  let cre_student = lib.create_student();
  console.log("create student: ", cre_student.name, cre_student.age)

  // Test struct class constructor
  let cre_teacher = new lib.Teacher();
  console.log("create teacher: ", cre_teacher.name, cre_teacher.age);
  let pro_teacher = lib.process_teacher(cre_teacher);
  console.log("process teacher: ", pro_teacher.name, pro_teacher.age);

  // Test struct class static function
  let lesson = lib.Teacher.give_lessons();
  console.log("teacher static function give lessons:", lesson);

  testDynamicInput("It is a string.");
  testDynamicInput({});
  testDynamicInput(null);

  let g = {f: 0, g: 0};
  let new_g = lib.process_g(g);
  let h = new lib.H(0, 0, 0);
  let new_h = lib.process_h(h);
  console.log("process g:", new_g.f, new_g.g);
  console.log("process h:", new_h.f, new_h.g, new_h.h);
}

main();
