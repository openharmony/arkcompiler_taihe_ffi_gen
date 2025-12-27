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

const lib = requireNapi('./opaque_test.so', RequireBaseDir.SCRIPT_DIR);

function main() {
    console.log("test opaque param", lib.is_string("test"));
    console.log("test opaque param", lib.is_string(2));

    console.log("test opaque return value", lib.get_object());

    let arr = lib.get_objects();
    if (arr[0] !== "FirstOne") throw new Error(`Unexpected result`);
    if (arr[1] !== undefined) throw new Error(`Unexpected result`);
    console.log("test opaque return array value", arr[0], arr[1]);

    let p: lib.Person = {name: "Mary"};
    console.log("test opaque param union", lib.is_opaque(p));
    console.log("test opaque param union", lib.is_opaque("1"));
}

main();
