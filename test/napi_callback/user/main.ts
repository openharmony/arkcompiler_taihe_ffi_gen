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

const lib = requireNapi('./cb_test.so', RequireBaseDir.SCRIPT_DIR);
let cb_value: number = -1;
let cb_str_value: string = "";
let cb_struct_value: lib.Data = {a: "", b: "", c: 0};
let cb_enum_value: lib.EnumData = lib.EnumData.F32_B;

function main() {
  lib.test_cb_v((): void => {
    cb_value = 0;
    console.log("test cb void success!")
  });
  if ( cb_value !== 0 ) throw new Error(`Unexpected result`);

  lib.test_cb_i((a: number): void => {
    cb_value = a;
    console.log("test cb int success! ", a)
  });
  if ( cb_value !== 1 ) throw new Error(`Unexpected result`);

  lib.test_cb_s((a: string): void => {
    cb_str_value = a;
    console.log("test cb string success! ", a)
  });
  if ( cb_str_value !== "hello" ) throw new Error(`Unexpected result`);

  let s = lib.test_cb_rs((a: string): string => {
    cb_str_value = a;
    console.log("test cb return string success! ")
    return "main success";
  });
  if ( cb_str_value !== "hello") throw new Error(`Unexpected result`);
  if ( s !== "main success") throw new Error(`Unexpected result`);

  lib.test_cb_struct((data: lib.Data): lib.Data => {
    console.log("test cb return string success! ")
    cb_struct_value = data;
    return {a: "a" + data.a, b: "b" + data.b, c: 3 + data.c};
  });
  if ( cb_struct_value.a !== "a" || cb_struct_value.b !== "b" || cb_struct_value.c !== 1 ) throw new Error(`Unexpected result`);
  
  let cb_str_res =  lib.test_x((): void => {
    console.log("test cb reverse success!")
  })("hello");
  if ( cb_str_res !== "CallbackReverse" ) throw new Error(`Unexpected result`);
  console.log(cb_str_res);

  let myiface = lib.getInterface();

  let cb_ret_str = myiface.testCbIntString((a: number, b: number): void => {
    cb_value = a + b;
    console.log("MyInterface TestCbIntString ", cb_value);
  })
  if ( cb_value !== 110 ) throw new Error(`Unexpected result`);
  if ( cb_ret_str !== "testCbIntString" ) throw new Error(`Unexpected result`);

  let cb_ret_bool = myiface.testCbIntBool((a: number, b: number): void => {
    cb_value = a + b;
    console.log("MyInterface TestCbIntBool ", cb_value);
  })
  if ( cb_value !== 200 ) throw new Error(`Unexpected result`);
  if ( cb_ret_bool !== true ) throw new Error(`Unexpected result`);

  let cb_ret_enum = myiface.testCbEnum((a: lib.EnumData): lib.EnumData => {
    cb_enum_value = a;
    console.log("MyInterface TestCbEnums ", a);
    return a;
  })
  if ( cb_enum_value !== lib.EnumData.F32_A ) throw new Error(`Unexpected result`);
  if ( cb_ret_enum !== lib.EnumData.F32_A ) throw new Error(`Unexpected result`);

  let cb_iface_ret_str = lib.test_cb_iface((a: lib.MyInterface): lib.MyInterface => {
    cb_str_value = a.testCbIntString((a: number, b: number): void => {
      cb_value = a + b;
      console.log("MyInterface TestCbIntString ", cb_value);
    });
    if ( cb_value !== 110 ) throw new Error(`Unexpected result`);
    console.log("test_cb_iface ", cb_str_value);
    return a;
  });
  if ( cb_str_value !== "testCbIntString" ) throw new Error(`Unexpected result`);
  if ( cb_iface_ret_str !== "test_cb_iface" ) throw new Error(`Unexpected result`);
}

main();
