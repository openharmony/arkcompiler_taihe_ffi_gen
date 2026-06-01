/*
 * Copyright (c) 2026 Huawei Device Co., Ltd.
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
import * as stringTest from "stringTest";

loadLibrary("ani_common_string");

function check_string_convert() {
    let output: string = stringTest.stringTest("aaa");
    console.log("stringTest output is " + output)
    arktest.assertEQ(output, "aaa")
}

function check_common_string() {
    let output: string = stringTest.commonStringTest();
    arktest.assertEQ(output, "common string test passed")
}

function main() {
    const suite = new arktest.ArkTestsuite("common string ut")
    suite.addTest("check string convert", check_string_convert)
    suite.addTest("check common string", check_common_string)
    exit(suite.run())
}
