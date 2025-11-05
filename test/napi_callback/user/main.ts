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

import * as lib from "cb_test";

function main() {
  lib.test_cb_v((): void => {
    console.log("test cb void success!")
  });
  lib.test_cb_i((a: number): void => {
    console.log("test cb int success! ", a)
  });
  lib.test_cb_s((a: string): void => {
    console.log("test cb string success! ", a)
  });
  let s = lib.test_cb_rs((a: string): string => {
    console.log("test cb return string success! ")
    return "main success";
  });
  if ( s !== "main success") throw new Error(`Unexpected result`);
  lib.test_cb_struct((data: lib.Data): lib.Data => {
    console.log("test cb return string success! ")
    return {a: "a" + data.a, b: "b" + data.b, c: 3 + data.c};
  });
  console.log(lib.test_x((): void => {
    console.log("test cb reverse success!")
  })("hello"));
}

main();
