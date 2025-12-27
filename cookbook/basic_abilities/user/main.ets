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
import * as basic_abilities from "basic_abilities";

loadLibrary("basic_abilities");
function main() {
    let input_arr: int[] = [1, 2, 3, 4, 5];
    let input_str: String = "hello";
    let output_arr: String[] =
        basic_abilities.convert_arr(input_arr, input_str);
    for (let i = 0; i < output_arr.length; i++) {
        console.log("arr [" + i + "] val " + output_arr[i])
    }
}
