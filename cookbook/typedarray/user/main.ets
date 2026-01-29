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
import * as typearr from "typedarray";

loadLibrary("typedarray");

function main() {
    // ets 侧创建，c++ 侧调用
    let arrbuf = new ArrayBuffer(8);
    arrbuf.set(0, (0xff).toByte());
    arrbuf.set(1, (0xff).toByte());
    arrbuf.set(2, (0x01).toByte());
    arrbuf.set(3, (0x00).toByte());
    let ets_uarr = new Uint16Array(arrbuf, 0, 2);
    typearr.printUint16Array(ets_uarr);

    // C++ 侧创建，ets 侧调用
    let c_uarr = typearr.createUint16Array();
    console.log(c_uarr);
}