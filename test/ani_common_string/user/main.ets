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

function check_u16_string_convert() {
    let output: string = stringTest.u16StringTest("Taihe 你好 😀");
    arktest.assertEQ(output, "Taihe 你好 😀")
}

function check_common_string_convert() {
    let output: string = stringTest.commonStringConvert("Common 你好 😀");
    arktest.assertEQ(output, "Common 你好 😀")
}

function check_u8_string() {
    let output: string = stringTest.taiheU8StrTest();
    arktest.assertEQ(output, "Taihe UTF-8 string test passed")
}

function check_u16_string() {
    let output: string = stringTest.taiheU16StrTest();
    arktest.assertEQ(output, "Taihe UTF-16 string test passed")
}

function check_common_string() {
    let output: string = stringTest.commonStringTest();
    arktest.assertEQ(output, "common string test passed")
}

const crossEncodingText = "Taihe 你好 😀 𠀀";

function check_projected_string_equality_and_hash() {
    arktest.assertTrue(stringTest.equalProjectedStrings(crossEncodingText, crossEncodingText))
}

function check_utf8_to_utf16_round_trip() {
    const output: string = stringTest.utf8ToUtf16(crossEncodingText);
    arktest.assertEQ(output, crossEncodingText)
}

function check_utf16_to_utf8_round_trip() {
    const output: string = stringTest.utf16ToUtf8(crossEncodingText);
    arktest.assertEQ(output, crossEncodingText)
}

function check_enums() {
    arktest.assertEQ(
        stringTest.u8StringEnumTest(stringTest.U8StringEnum.FOO),
        stringTest.U8StringEnum.BAR);
    arktest.assertEQ(
        stringTest.u16StringEnumTest(stringTest.U16StringEnum.FOO),
        stringTest.U16StringEnum.BAR);
    arktest.assertEQ(
        stringTest.commonStringEnumTest(stringTest.CommonStringEnum.FOO),
        stringTest.CommonStringEnum.BAR);
}

function main() {
    const suite = new arktest.ArkTestsuite("common string ut")
    suite.addTest("check string convert", check_string_convert)
    suite.addTest("check u16 string convert", check_u16_string_convert)
    suite.addTest("check common string convert", check_common_string_convert)
    suite.addTest("check taihe::string func", check_u8_string)
    suite.addTest("check taihe::u16string func", check_u16_string)
    suite.addTest("check common string", check_common_string)
    suite.addTest("check projected string equality and hash", check_projected_string_equality_and_hash)
    suite.addTest("check UTF-8 to UTF-16 round trip", check_utf8_to_utf16_round_trip)
    suite.addTest("check UTF-16 to UTF-8 round trip", check_utf16_to_utf8_round_trip)
    suite.addTest("check enums", check_enums)
    exit(suite.run())
}
