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
import * as javalike_overload from "javalike_overload";

loadLibrary("javalike_overload");

function main() {
    let a: int = 1
    let b: int = 2
    let numbers: int[] = [1, 2, 3, 4, 5];
    console.log("add_two: " + javalike_overload.add(a, b))
    console.log("add_arr: " + javalike_overload.add(numbers))
}