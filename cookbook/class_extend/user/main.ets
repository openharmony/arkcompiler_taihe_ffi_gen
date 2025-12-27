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

loadLibrary("class_extend");

function main() {
    let a = new hello.UnifiedRecord();
    let x1 = new hello.UnifiedData(a);
    x1.addRecord(a);
    let y1 = x1.getRecords();
    y1[0].getType();

    let b = new hello.Text();
    b.getType();
    b.getDetails();
    let x2 = new hello.UnifiedData(b);
    x2.addRecord(a);
    let y2 = x2.getRecords();
    y2[0].getType();

    let c = new hello.PlainText();
    c.getType();
    c.getDetails();
    c.getTextContent();
    let x3 = new hello.UnifiedData(c);
    x3.addRecord(a);
    let y3 = x3.getRecords();
    y3[0].getType();
}
