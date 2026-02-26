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
import {MyInterface, MyStruct, UIAbility, useUIAbility} from "class_test";

loadLibrary("class");

class MyAbility extends UIAbility {
    constructor() {
        super();
    }
    onForeground(): void {
        console.log("in ets onForeground")
    }
}

function main() {
    let my_uiability: UIAbility = new MyAbility();
    useUIAbility(my_uiability);
    MyAbility.logLifecycle("using uiability")

    // Static method
    let staticMsg = MyStruct.staticFunc();
    console.log(staticMsg);

    // Constructor
    let myInstance = new MyInterface();
    let interfaceMsg = myInstance.doSomething("Taihe");
    console.log(interfaceMsg);
}