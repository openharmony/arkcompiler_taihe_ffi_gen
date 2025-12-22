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
import {cbCompare} from "cb_compare";

loadLibrary("callback_compare");

function main() {
    let callback_1 = () => {
        console.log("Callback 1 executed");
        return "Callback 1 result";
    };
    let callback_2 = () => {
        console.log("Callback 2 executed");
        return "Callback 2 result";
    };
    console.log("same callback: " + cbCompare(callback_1, callback_1))
    console.log("different callback: " + cbCompare(callback_1, callback_2))
}