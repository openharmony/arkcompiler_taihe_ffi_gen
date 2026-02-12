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
import * as RenameTest from "rename_test";

loadLibrary("ani_rename");

function test_rename_function() {
    // Function renamed from "oldAdd" to "add"
    let result = RenameTest.add(3, 4);
    arktest.assertEQ(result, 7);
}

function test_rename_enum_type() {
    // Enum type renamed from "OldColor" to "Color"
    let c: RenameTest.Color = RenameTest.Color.red;
    let val = RenameTest.getColorValue(c);
    arktest.assertEQ(val, 0);
}

function test_rename_enum_items() {
    // Enum items renamed: RED->red, GREEN->green, BLUE->blue
    arktest.assertEQ(RenameTest.getColorValue(RenameTest.Color.red), 0);
    arktest.assertEQ(RenameTest.getColorValue(RenameTest.Color.green), 1);
    arktest.assertEQ(RenameTest.getColorValue(RenameTest.Color.blue), 2);
}

function test_rename_const_enum() {
    // OLD_ZERO->ZERO
    arktest.assertEQ(RenameTest.INT_MAX, 2147483647);
    arktest.assertEQ(RenameTest.ZERO, 0);
}

function test_rename_struct_type() {
    // Struct type renamed from "OldPoint" to "Point"
    let p: RenameTest.Point = RenameTest.createPoint(10, 20);
    let sum = RenameTest.getPointSum(p);
    arktest.assertEQ(sum, 30);
}

function test_rename_struct_fields() {
    // Struct fields renamed: x->xPos, y->yPos
    let p = RenameTest.createPoint(5, 15);
    arktest.assertEQ(p.xPos, 5);
    arktest.assertEQ(p.yPos, 15);
}

function test_rename_struct_construct() {
    // Construct struct using renamed field names
    let p: RenameTest.Point = {xPos: 100, yPos: 200};
    let sum = RenameTest.getPointSum(p);
    arktest.assertEQ(sum, 300);
}

function test_rename_interface() {
    // Interface renamed from "OldCalculator" to "Calculator"
    // Method renamed from "oldCompute" to "compute"
    let calc: RenameTest.Calculator = RenameTest.createCalculator();
    let result = calc.compute(6, 7);
    arktest.assertEQ(result, 42);
}

function test_rename_union() {
    // Union type renamed from "OldData" to "Data"
    let intData: RenameTest.Data = RenameTest.createIntData(42);
    let strData: RenameTest.Data = RenameTest.createStrData("hello");
}

function main() {
    console.log("############## ani_rename start #############");
    const suite = new arktest.ArkTestsuite("Rename Tests");

    suite.addTest("test_rename_function", test_rename_function);
    suite.addTest("test_rename_enum_type", test_rename_enum_type);
    suite.addTest("test_rename_enum_items", test_rename_enum_items);
    suite.addTest("test_rename_const_enum", test_rename_const_enum);
    suite.addTest("test_rename_struct_type", test_rename_struct_type);
    suite.addTest("test_rename_struct_fields", test_rename_struct_fields);
    suite.addTest("test_rename_struct_construct", test_rename_struct_construct);
    suite.addTest("test_rename_interface", test_rename_interface);
    suite.addTest("test_rename_union", test_rename_union);

    exit(suite.run());
}
