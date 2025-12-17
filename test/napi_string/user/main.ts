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

const lib = requireNapi('./string_test.so', RequireBaseDir.SCRIPT_DIR);

function main() {
  let concat_str = lib.concat("test", "concat");
  if (concat_str !== "testconcat") throw new Error(`Unexpected result`);
  console.log("function concat: ", concat_str);

  let i32_from_str = lib.to_i32("test");
  if (i32_from_str !== 0) throw new Error(`Unexpected result`);
  console.log("function to_i32: ", i32_from_str);
  
  let str_from_i32 = lib.from_i32(20);
  if (str_from_i32 !== "20") throw new Error(`Unexpected result`);
  console.log("function from_i32: ", str_from_i32);
  
  let str_show = lib.show();
  console.log("function show: ", str_show);

  let add_show = lib.add(2, 3);
  if (add_show !== 5) throw new Error(`Unexpected result`);
  console.log("function add: ", add_show);

  let sum_show = lib.sum(2, 3);
  if (sum_show !== 6) throw new Error(`Unexpected result`);
  console.log("function sum: ", sum_show);
}

main();
