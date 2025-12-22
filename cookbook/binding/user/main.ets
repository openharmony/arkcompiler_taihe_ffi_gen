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
import * as binding from "binding";

loadLibrary("binding");
function main() {
    let Color1: binding.Color = {R: 0, G: 255, B: 255};
    console.log("Color1 is " + Color1.R + " " + Color1.G + " " + Color1.B)
    let Color2 = binding.convert_color(Color1)
    console.log("Color2 is " + Color2.R + " " + Color2.G + " " + Color2.B)
}