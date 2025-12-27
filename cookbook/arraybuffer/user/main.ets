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
import * as arraybuffer from "arraybuffer";

loadLibrary("arraybuffer");
function main() {
    let numbersU8: byte[] = [1, 1, 0, 0, 0];
    let arrbuf1: ArrayBuffer = new ArrayBuffer(numbersU8.length);
    for (let i = 0; i < numbersU8.length; i++) {
        arrbuf1.set(i, numbersU8[i]);
    }
    let num1 = arraybuffer.convert2Int(arrbuf1);
    console.log("num1: " + num1);

    // let arrbuf2: ArrayBuffer = new ArrayBuffer(3);
    // for (let i = 0; i < 3; i++) {
    //     arrbuf2.set(i, numbersU8[i]);
    // }
    // let num2 = arraybuffer.convert2Int(arrbuf2);
    // console.log("num2: " + num2);
}
