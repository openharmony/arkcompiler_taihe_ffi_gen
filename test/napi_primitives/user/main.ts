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

const lib = requireNapi('./primitives_test.so', RequireBaseDir.SCRIPT_DIR);

function main() {
  let i32_res = lib.func1(10);
  if (i32_res !== 11) throw new Error(`Unexpected result`);
  console.log("function func1: ", i32_res);

  let i64_res = lib.func2(20);
  if (i64_res !== 21) throw new Error(`Unexpected result`);
  console.log("function func2: ", i64_res);

  let u32_res = lib.func3(30);
  if (u32_res !== 31) throw new Error(`Unexpected result`);
  console.log("function func3: ", u32_res);

  let f64_res = lib.func4(1.5);
  if (f64_res !== 2.5) throw new Error(`Unexpected result`);
  console.log("function func4: ", f64_res);

  let bool_res = lib.func5(true);
  if (bool_res !== false) throw new Error(`Unexpected result`);
  console.log("function func5: ", bool_res);
}

main();
