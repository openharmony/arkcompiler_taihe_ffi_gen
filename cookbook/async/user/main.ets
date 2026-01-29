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
import * as async_test from "async";

loadLibrary("async");
function main() {
    console.log("addSync: ", async_test.addSync(1, 2))

    async_test.add(10, 20, (error: BusinessError|null, data?: int) => {
        if (error !== null && error.code !== 0) {
            console.log("async ERROR ", error);
        } else {
            console.log("async success ", data);
        }
    })

    try {
        let retPromise = await async_test.add(0, 2);
        console.log("async promise success ")
    } catch (error) {
        console.error("async promise ERROR ", error)
    }


    // async interface method example
    let istringholder = async_test.makeIStringHolder();
    console.log(istringholder.newGet());

    istringholder.setStr("interface async set", (error: BusinessError|null) => {
        if (error !== null && error.code !== 0) {
            console.log("interface async ERROR ", error);
        } else {
            console.log("interface async success ");
        }
    })

    let p_istringholder = istringholder.getStrRetPromise();
    p_istringholder
        .then((ret: Any) => {
            let retInner = ret as string;
            console.log("interface async success p_istringholder ", retInner)
        })
        .catch((ret: Any) => {
            let retError = ret as Error;
            console.error(
                "interface async promise ERROR p_istringholder ", retError)
        });

    CoroutineExtras.stopTaskpool();
    // temporary workaround for the problem that multiple processes cannot exit
    exit(0)
}