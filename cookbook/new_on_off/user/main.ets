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
import * as OnOff from "on_off";

loadLibrary("new_on_off");

function main() {
    let num0: Int = 0;
    let num1: Int = 1;
    let obj = OnOff.getISetterObserver();
    obj.on("set", (): void => {
        console.log("ISetterObserver onSet callback");
    });
    obj.off("set", (): void => {
        console.log("ISetterObserver offSet callback");
    });
    OnOff.on("foo", (): void => {
        console.log("onFoo callback");
    });
    OnOff.on("bar", (): void => {
        console.log("onBar callback");
    });
    OnOff.on("newBaz", num1, (arg0: Int): void => {
        console.log("onNewBaz callback, num: " + arg0);
    });
    OnOff.off("foo", (): void => {
        console.log("offFoo callback");
    });
    OnOff.off("bar", (): void => {
        console.log("offBar callback");
    });
    OnOff.off("newBaz", num0, (arg0: Int): void => {
        console.log("offNewBaz callback, num: " + arg0);
    });
}