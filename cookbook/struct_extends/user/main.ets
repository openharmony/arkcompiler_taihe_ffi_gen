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
import * as structext from "structext";

loadLibrary("struct_extends");

function main() {
    let Player1 = structext.addNewPlayer("Tom");
    let Player2 = structext.addNewPlayer("Jimmy");
    console.log("Player1's name is " + Player1.name);
    console.log("Player2's name is " + Player2.name);
    Player2.x += 1;
    Player2.y += 1;
    Player2.z += 1;
    console.log(
        "Player1's position is " + Player1.x + "," + Player1.y + "," +
        Player1.z);
    console.log(
        "Player2's position is " + Player2.x + "," + Player2.y + "," +
        Player2.z);
}