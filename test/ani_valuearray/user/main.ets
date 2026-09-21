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

import * as hello from "hello";

loadLibrary("ani_valuearray");

function testValueArrayInt(
    test: hello.TestInterface, intArray: ValueArray<int>) {
    test.setValueArrayInt(intArray);
    let result = test.getValueArrayInt();
    arktest.assertEQ(intArray.length, result.length);
    for (let i = 0; i < intArray.length; i++) {
        arktest.assertEQ(intArray[i], result[i]);
    }
}

function testValueArrayDouble(
    test: hello.TestInterface, doubleArray: ValueArray<double>) {
    test.setValueArrayDouble(doubleArray);
    let result = test.getValueArrayDouble();
    arktest.assertEQ(doubleArray.length, result.length);
    for (let i = 0; i < doubleArray.length; i++) {
        arktest.assertEQ(doubleArray[i], result[i]);
    }
}

function testValueArrayBoolean(
    test: hello.TestInterface, booleanArray: ValueArray<boolean>) {
    test.setValueArrayBoolean(booleanArray);
    let result = test.getValueArrayBoolean();
    arktest.assertEQ(booleanArray.length, result.length);
    for (let i = 0; i < booleanArray.length; i++) {
        arktest.assertEQ(booleanArray[i], result[i]);
    }
}

function main() {
    const suite = new arktest.ArkTestsuite("ValueArray Test");

    let test = new hello.TestInterface();

    suite.addTest("ValueArrayInt", () => {
        testValueArrayInt(test, [1, 2, 3, 4, 5]);
    });
    suite.addTest("ValueArrayDouble", () => {
        testValueArrayDouble(test, [1.1, 2.2, 3.3]);
    });
    suite.addTest("ValueArrayBoolean", () => {
        testValueArrayBoolean(test, [true, false]);
    });

    exit(suite.run());
}