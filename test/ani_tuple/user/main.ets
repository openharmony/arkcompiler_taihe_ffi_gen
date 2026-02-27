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
import * as TupleTest from "tuple_test";

loadLibrary("ani_tuple");

// ====== Test 1: IntPair - basic creation and return ======
function testMakeIntPair() {
    let pair: TupleTest.IntPair = TupleTest.makeIntPair(10, 20);
    console.log("makeIntPair: [" + pair[0] + ", " + pair[1] + "]");
    arktest.assertEQ(pair[0], 10);
    arktest.assertEQ(pair[1], 20);
}

// ====== Test 2: IntPair - pass in and compute ======
function testSumIntPair() {
    let pair: TupleTest.IntPair = [3, 7];
    let sum = TupleTest.sumIntPair(pair);
    console.log("sumIntPair: " + sum);
    arktest.assertEQ(sum, 10);
}

// ====== Test 3: IntPair - roundtrip (pass in and return) ======
function testSwapIntPair() {
    let pair: TupleTest.IntPair = [100, 200];
    let swapped = TupleTest.swapIntPair(pair);
    console.log("swapIntPair: [" + swapped[0] + ", " + swapped[1] + "]");
    arktest.assertEQ(swapped[0], 200);
    arktest.assertEQ(swapped[1], 100);
}

// ====== Test 4: MixedTuple - all primitive types ======
function testProcessMixed() {
    let m: TupleTest.MixedTuple = [
        (1 as byte),   // i8
        (2 as short),  // i16
        3,             // i32
        4 as long,     // i64
        5.0f,          // f32
        6.0,           // f64
        true,          // bool
    ];
    let result = TupleTest.processMixed(m);
    console.log(
        "processMixed: [" + result[0] + ", " + result[1] + ", " + result[2] +
        ", " + result[3] + ", " + result[4] + ", " + result[5] + ", " +
        result[6] + "]");
    arktest.assertEQ(result[0], (2 as byte));
    arktest.assertEQ(result[1], (4 as short));
    arktest.assertEQ(result[2], 6);
    arktest.assertEQ(result[3], 8 as long);
    // float comparison
    arktest.assertTrue(result[4] > 9.9f && result[4] < 10.1f);
    arktest.assertTrue(result[5] > 11.9 && result[5] < 12.1);
    arktest.assertEQ(result[6], false);
}

// ====== Test 5: StringPair - string types in tuple ======
function testMakeStringPair() {
    let pair = TupleTest.makeStringPair("hello", "world");
    console.log("makeStringPair: [" + pair[0] + ", " + pair[1] + "]");
    arktest.assertEQ(pair[0], "hello");
    arktest.assertEQ(pair[1], "world");
}

function testConcatStringPair() {
    let pair: TupleTest.StringPair = ["foo", "bar"];
    let result = TupleTest.concatStringPair(pair);
    console.log("concatStringPair: " + result);
    arktest.assertEQ(result, "foo:bar");
}

// ====== Test 6: MixedRefTuple - mixed ref and primitive types ======
function testMakeMixedRef() {
    let t = TupleTest.makeMixedRef("Alice", 30, 95.5, true);
    console.log(
        "makeMixedRef: [" + t[0] + ", " + t[1] + ", " + t[2] + ", " + t[3] +
        "]");
    arktest.assertEQ(t[0], "Alice");
    arktest.assertEQ(t[1], 30);
    arktest.assertTrue(t[2] > 95.4 && t[2] < 95.6);
    arktest.assertEQ(t[3], true);
}

function testDescribeMixedRef() {
    let t: TupleTest.MixedRefTuple = ["Bob", 25, 88.0, false];
    let desc = TupleTest.describeMixedRef(t);
    console.log("describeMixedRef: " + desc);
    arktest.assertEQ(desc, "Bob,25,88,false");
}

// ====== Test 7: Array<IntPair> - tuple as Array element ======
function testMakeIntPairArray() {
    let arr: Array<TupleTest.IntPair> = TupleTest.makeIntPairArray(3);
    console.log("makeIntPairArray length: " + arr.length);
    arktest.assertEQ(arr.length, 3);
    // arr[0] = [0, 0], arr[1] = [1, 10], arr[2] = [2, 20]
    arktest.assertEQ(arr[0][0], 0);
    arktest.assertEQ(arr[0][1], 0);
    arktest.assertEQ(arr[1][0], 1);
    arktest.assertEQ(arr[1][1], 10);
    arktest.assertEQ(arr[2][0], 2);
    arktest.assertEQ(arr[2][1], 20);
}

function testSumIntPairArray() {
    let arr: Array<TupleTest.IntPair> = [[1, 2], [3, 4], [5, 6]];
    let total = TupleTest.sumIntPairArray(arr);
    console.log("sumIntPairArray: " + total);
    // 1+2+3+4+5+6 = 21
    arktest.assertEQ(total, 21);
}

// ====== Test 8: ArrayTuple - tuple containing an Array ======
function testMakeArrayTuple() {
    let t = TupleTest.makeArrayTuple("data", 3);
    console.log("makeArrayTuple: [" + t[0] + ", " + t[1] + "]");
    arktest.assertEQ(t[0], "data");
    arktest.assertEQ(t[1].length, 3);
    // values: [10, 20, 30]
    arktest.assertEQ(t[1][0], 10);
    arktest.assertEQ(t[1][1], 20);
    arktest.assertEQ(t[1][2], 30);
}

function testSumArrayTuple() {
    let values: int[] = [10, 20, 30];
    let t: TupleTest.ArrayTuple = ["result", values];
    let desc = TupleTest.sumArrayTuple(t);
    console.log("sumArrayTuple: " + desc);
    arktest.assertEQ(desc, "result:60");
}

function testTransposeMyTuple4x4() {
    let a: TupleTest.MyTuple4 = [1, 2, 3, 4];
    let b: TupleTest.MyTuple4 = [5, 6, 7, 8];
    let c: TupleTest.MyTuple4 = [9, 10, 11, 12];
    let d: TupleTest.MyTuple4 = [13, 14, 15, 16];
    let t: TupleTest.MyTuple4x4 = [a, b, c, d];
    let transposed = TupleTest.transposeMyTuple4x4(t);
    arktest.assertEQ(transposed[0][0], t[0][0]);
    arktest.assertEQ(transposed[0][1], t[1][0]);
    arktest.assertEQ(transposed[0][2], t[2][0]);
    arktest.assertEQ(transposed[0][3], t[3][0]);
    arktest.assertEQ(transposed[1][0], t[0][1]);
    arktest.assertEQ(transposed[1][1], t[1][1]);
    arktest.assertEQ(transposed[1][2], t[2][1]);
    arktest.assertEQ(transposed[1][3], t[3][1]);
    arktest.assertEQ(transposed[2][0], t[0][2]);
    arktest.assertEQ(transposed[2][1], t[1][2]);
    arktest.assertEQ(transposed[2][2], t[2][2]);
    arktest.assertEQ(transposed[2][3], t[3][2]);
    arktest.assertEQ(transposed[3][0], t[0][3]);
    arktest.assertEQ(transposed[3][1], t[1][3]);
    arktest.assertEQ(transposed[3][2], t[2][3]);
    arktest.assertEQ(transposed[3][3], t[3][3]);
}

function testTransposeMyTuple4Array() {
    let t: TupleTest.MyTuple4Array = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 16],
    ];
    let transposed = TupleTest.transposeMyTuple4Array(t);
    for (let i = 0; i < 4; i++) {
        arktest.assertEQ(transposed[i][0], t[0][i]);
        arktest.assertEQ(transposed[i][1], t[1][i]);
        arktest.assertEQ(transposed[i][2], t[2][i]);
        arktest.assertEQ(transposed[i][3], t[3][i]);
    }
}

function testTransposeArrayMyTuple4() {
    let t: Array<TupleTest.MyTuple4> = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 16],
    ];
    let transposed = TupleTest.transposeArrayMyTuple4(t);
    for (let i = 0; i < 4; i++) {
        arktest.assertEQ(transposed[0][i], t[i][0]);
        arktest.assertEQ(transposed[1][i], t[i][1]);
        arktest.assertEQ(transposed[2][i], t[i][2]);
        arktest.assertEQ(transposed[3][i], t[i][3]);
    }
}

function testMakeMyTuple16() {
    let t = TupleTest.makeMyTuple16(
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16);
    arktest.assertEQ(t[0], 1);
    arktest.assertEQ(t[1], 2);
    arktest.assertEQ(t[2], 3);
    arktest.assertEQ(t[3], 4);
    arktest.assertEQ(t[4], 5);
    arktest.assertEQ(t[5], 6);
    arktest.assertEQ(t[6], 7);
    arktest.assertEQ(t[7], 8);
    arktest.assertEQ(t[8], 9);
    arktest.assertEQ(t[9], 10);
    arktest.assertEQ(t[10], 11);
    arktest.assertEQ(t[11], 12);
    arktest.assertEQ(t[12], 13);
    arktest.assertEQ(t[13], 14);
    arktest.assertEQ(t[14], 15);
    arktest.assertEQ(t[15], 16);
}

function testSumMyTuple16() {
    let t: TupleTest.MyTuple16 =
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16];
    let sum = 0;
    sum += t[0];
    sum += t[1];
    sum += t[2];
    sum += t[3];
    sum += t[4];
    sum += t[5];
    sum += t[6];
    sum += t[7];
    sum += t[8];
    sum += t[9];
    sum += t[10];
    sum += t[11];
    sum += t[12];
    sum += t[13];
    sum += t[14];
    sum += t[15];
    let result = TupleTest.sumMyTuple16(t);
    console.log("sumMyTuple16: " + result);
    arktest.assertEQ(result, sum);
}

// ====== Run all tests ======
function main() {
    const suite = new arktest.ArkTestsuite("Tuple Tests");

    suite.addTest("MakeIntPair", testMakeIntPair);
    suite.addTest("SumIntPair", testSumIntPair);
    suite.addTest("SwapIntPair", testSwapIntPair);
    suite.addTest("ProcessMixed", testProcessMixed);
    suite.addTest("MakeStringPair", testMakeStringPair);
    suite.addTest("ConcatStringPair", testConcatStringPair);
    suite.addTest("MakeMixedRef", testMakeMixedRef);
    suite.addTest("DescribeMixedRef", testDescribeMixedRef);
    suite.addTest("MakeIntPairArray", testMakeIntPairArray);
    suite.addTest("SumIntPairArray", testSumIntPairArray);
    suite.addTest("MakeArrayTuple", testMakeArrayTuple);
    suite.addTest("SumArrayTuple", testSumArrayTuple);
    suite.addTest("TransposeMyTuple4x4", testTransposeMyTuple4x4);
    suite.addTest("TransposeMyTuple4Array", testTransposeMyTuple4Array);
    suite.addTest("TransposeArrayMyTuple4", testTransposeArrayMyTuple4);
    suite.addTest("MakeMyTuple16", testMakeMyTuple16);
    suite.addTest("SumMyTuple16", testSumMyTuple16);

    exit(suite.run());
}
