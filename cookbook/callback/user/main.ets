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

import {BusinessError} from "@ohos.base";
import * as callback_lib from "callback";

loadLibrary("callback");

function main() {
    callback_lib.cb_void_void(() => {
        console.log("void input void output callback!");
    });
    callback_lib.cb_i_void((a: int) => {
        console.log("int input void output callback! input is: ", a);
    });
    let result = callback_lib.cb_str_str((a: string) => {
        console.log("param a is: ", a);
        return "my return value";
    });
    console.log("global function output: ", result);
    callback_lib.cb_struct((a: callback_lib.Person) => {
        let person: callback_lib.Person = {
            name: (a.name + " Swift"),
            age: (a.age + 18)
        };
        return person;
    });
}
