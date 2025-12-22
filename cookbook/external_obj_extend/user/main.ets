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

import * as lib from "external_obj_extend";
import {Context} from "other.subsystem";

loadLibrary("external_obj_extend");

function main() {
    let context = new Context();
    console.log("base class: ", context.start(), " ", context.stop());
    let mycontext = new lib.MyContext();
    console.log("sub class: ", mycontext.start(), " ", mycontext.stop());
}