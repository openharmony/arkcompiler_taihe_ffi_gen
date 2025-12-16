/*
 * Copyright (c) 2025 Huawei Device Co., Ltd.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

const lib = requireNapi('./struct_test.so', RequireBaseDir.SCRIPT_DIR);

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
  if (my_rgb.r !== 16 && my_rgb.g != 8 && my_rgb.b != 4) throw new Error(`Unexpected result`);
  console.log("i32 to ts rgb: ", my_rgb.r, my_rgb.g, my_rgb.b);
  let my_rgb_i32 = lib.from_rgb(my_rgb);
  if (my_rgb_i32 !== 28) throw new Error(`Unexpected result`);
  console.log("from ts RGB to i32: ", my_rgb_i32);

  let my_color = lib.to_color("white", true, 3.12, my_rgb);
  if (my_color.name !== "white" && my_color.flag !== true && my_color.price !== 3.12 && my_color.rgb.r !== 16) throw new Error(`Unexpected result`);
  console.log("f64 to ts color: ", my_color.name, my_color.flag, my_color.price, my_color.rgb.r);
  let my_color_f64 = lib.from_color(my_color);
  if (my_color_f64 !== 116) throw new Error(`Unexpected result`);
  console.log("from ts color to f64: ", my_color_f64);

  let student: lib.Student = {name: "Jack", age: 10};
  let pro_student = lib.process_student(student);
  if (pro_student.name !== "Jack student" && pro_student.age !== 20) throw new Error(`Unexpected result`);
  console.log("process student: ", pro_student.name, pro_student.age)
  let cre_student = lib.create_student();
  if (cre_student.name !== "Mary" && cre_student.age !== 15) throw new Error(`Unexpected result`);
  console.log("create student: ", cre_student.name, cre_student.age)

  // Test struct class constructor
  let cre_teacher = new lib.Teacher();
  if (cre_teacher.name !== "Rose" && cre_teacher.age !== 25) throw new Error(`Unexpected result`);
  console.log("create teacher: ", cre_teacher.name, cre_teacher.age);
  let pro_teacher = lib.process_teacher(cre_teacher);
  if (pro_teacher.name !== "Rose teacher" && pro_teacher.age !== 40) throw new Error(`Unexpected result`);
  console.log("process teacher: ", pro_teacher.name, pro_teacher.age);

  // Test struct class static function
  let lesson = lib.Teacher.give_lessons();
  if (lesson !== "math") throw new Error(`Unexpected result`);
  console.log("teacher static function give lessons:", lesson);

  testDynamicInput("It is a string.");
  testDynamicInput({});
  testDynamicInput(null);

  let g = {f: 0, g: 0};
  let new_g = lib.process_g(g);
  let h = new lib.H(0, 0, 0);
  let new_h = lib.process_h(h);
  if (new_g.f !== 1 && new_g.g !== 2) throw new Error(`Unexpected result`);
  console.log("process g:", new_g.f, new_g.g);
  if (new_h.f !== 1 && new_h.g !== 2 && new_h.h !== 3) throw new Error(`Unexpected result`);
  console.log("process h:", new_h.f, new_h.g, new_h.h);
}

main();
