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
import * as rename_example from "rename_example";

loadLibrary("rename_example");

function main() {
    // Function: ArkTS uses renamed name "newFoo", C++ uses original "oldFoo"
    let res = rename_example.newFoo(1, 2);
    console.log("newFoo(1, 2) = " + res);

    // Enum: type renamed to "Color", items renamed to "red", "green", "blue"
    let c: rename_example.Color = rename_example.Color.red;
    console.log("Color.red = " + c);

    // Struct: type renamed to "Point", fields renamed to "xPos", "yPos"
    let p = rename_example.createPoint(10, 20);
    console.log("Point.xPos = " + p.xPos + ", Point.yPos = " + p.yPos);

    // Interface: type renamed to "Greeter"
    let g: rename_example.Greeter = rename_example.createGreeter("Taihe");
    console.log(g.greet());

    // Parameter rename: parameter "msg" renamed to "message"
    let msg = rename_example.testParamRename("Hello, Taihe!");
    console.log(msg);

    // Static method
    let staticMsg = rename_example.MyStruct.staticFunc();
    console.log(staticMsg);

    // Constructor
    let myInstance = new rename_example.MyInterface();
    let interfaceMsg = myInstance.doSomething("Taihe");
    console.log(interfaceMsg);
}
