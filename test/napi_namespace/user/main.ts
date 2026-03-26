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

const lib_a = requireNapi('./my_module_a.so', RequireBaseDir.SCRIPT_DIR);
const lib_b = requireNapi('./my_module_b.so', RequireBaseDir.SCRIPT_DIR);


function main() {
    let a = lib_a.ns1.Color.BLUE;
    let res_f = lib_a.ns1.Funtest(a);
    if (res_f !== "blue") throw new Error(`Unexpected result`);
    console.log(res_f);
    let s: lib_a.ns1.ns2.ns3.ns4.ns5.MyStruct = {a: 1, b: 2};
    console.log(lib_a.ns1.ns2.ns3.ns4.ns5.Funtest(s));
    let iabse = lib_b.functiontest.makeIBase("aaaaa");
    console.log(iabse.getId());

    lib_a.baz();
    lib_a.ns1.noo();
    lib_a.ns1.ns2.ns3.ns4.ns5.foo();
    lib_b.functiontest.bar();
}
main();