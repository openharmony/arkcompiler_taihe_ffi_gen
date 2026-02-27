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
import * as st from "struct_tuple";

loadLibrary("struct_tuple");

function main() {
    // ===== 基础 struct：通过属性名访问字段 =====
    let red = st.makeColor(255, 0, 0);
    let blue = st.makeColor(0, 0, 255);
    console.log("red: r=" + red.r + " g=" + red.g + " b=" + red.b);
    // red: r=255 g=0 b=0

    let purple = st.mixColors(red, blue);
    console.log("purple: r=" + purple.r + " g=" + purple.g + " b=" + purple.b);
    // purple: r=127 g=0 b=127

    // ===== @tuple struct：通过下标访问字段 =====
    let p1 = st.makePoint(0.0, 0.0);
    let p2 = st.makePoint(3.0, 4.0);
    console.log("p1: [" + p1[0] + ", " + p1[1] + "]");
    // p1: [0, 0]
    console.log("p2: [" + p2[0] + ", " + p2[1] + "]");
    // p2: [3, 4]
    console.log("distance: " + st.distance(p1, p2));
    // distance: 5

    // @tuple 也可以用字面量构造
    let p3: st.Point = [1.0, 1.0];
    console.log("distance p2-p3: " + st.distance(p2, p3));
    // distance p2-p3: 3.605551275463989

    // 包含引用类型的 @tuple
    let np = st.makeNamedPoint("origin", 0.0, 0.0);
    console.log("name: " + np[0] + " x: " + np[1] + " y: " + np[2]);
    // name: origin x: 0 y: 0
    console.log(st.describePoint(np));
    // origin(0, 0)

    // ===== @tuple 嵌套 =====
    let seg = st.makeSegment(0.0, 0.0, 3.0, 4.0);
    // seg[0] 是 start Point, seg[1] 是 end Point
    console.log("start: [" + seg[0][0] + ", " + seg[0][1] + "]");
    // start: [0, 0]
    console.log("end: [" + seg[1][0] + ", " + seg[1][1] + "]");
    // end: [3, 4]
    console.log("length: " + st.segmentLength(seg));
    // length: 5

    // ===== Array<@tuple> =====
    let points = st.makePointArray(4);
    for (let i = 0; i < points.length; i++) {
        console.log(
            "points[" + i + "]: [" + points[i][0] + ", " + points[i][1] + "]");
    }
    // points[0]: [0, 0]
    // points[1]: [1, 1]
    // points[2]: [2, 4]
    // points[3]: [3, 9]
}
