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
import {ICalculator, makeCalculator, restartCalculator} from "interface";

loadLibrary("interface");
function main() {
    let cal = makeCalculator();
    let num1 = 1;
    let num2 = 2;
    let result1 = cal.add(num1, num2);
    console.log("num1 + num2 = " + result1);
    let result2 = cal.sub(num1, num2);
    console.log("num1 - num2 = " + result2);
    let result3 = cal.getLastResult();
    console.log("Last calculation result: " + result3);
    console.log("--- restartCalculator ---");
    restartCalculator(cal);
    let result4 = cal.getLastResult();
    console.log("Last calculation result: " + result4);
}
