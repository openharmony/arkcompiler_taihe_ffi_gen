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

  let color_new = new lib.Color("hello", true, 1.314, rgb);
  console.log("new color", color_new.name, color_new.flag, color_new.price, color_new.rgb.r);
  let my_color = lib.to_color("white", true, 3.12, my_rgb);
  console.log("f64 to ts color: ", my_color.name, my_color.flag, my_color.price, my_color.rgb.r);
  let my_color_f64 = lib.from_color(color_new);
  console.log("from ts color to f64: ", my_color_f64);

  let student: lib.Student = {name: "Jack", age: 10};
  let pro_student = lib.process_student(student);
  console.log("process student: ", pro_student.name, pro_student.age)
  let cre_student = lib.create_student();
  console.log("create student: ", cre_student.name, cre_student.age)

  let teacher: lib.Teacher = {name: "Jony", age: 30};
  let pro_teacher = lib.process_teacher(teacher);
  console.log("process teacher: ", pro_teacher.name, pro_teacher.age)
  let cre_teacher = lib.create_teacher();
  console.log("create teacher: ", cre_teacher.name, cre_student.age)

  testDynamicInput("It is a string.");
  testDynamicInput({});
  testDynamicInput(null);
}

main();
