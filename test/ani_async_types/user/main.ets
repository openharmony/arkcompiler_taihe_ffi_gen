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
import * as hello from "hello";

loadLibrary("ani_async_types");

function test_returns_promise(): void {
    let x = hello.futureResultReturnsPromise(1000, "Hello, World!");
    console.log("Waiting for result...");
    waitForCompletion(() => x.then((s: String) => {
        console.log("Promise Result: " + s);
    }));
}

function test_with_callback(): void {
    let x = new Promise<string>((resolve, reject) => {
        hello.futureResultWithCallback(
            1000, "Hello, Callback!",
            (err: BusinessError|null, res: String|undefined) => {
                resolve(res!);
            });
    });
    console.log("Waiting for callback...");
    waitForCompletion(() => x.then((s: String) => {
        console.log("Callback Result: " + s);
    }));
}

function main(): void {
    const suite = new arktest.ArkTestsuite("Hello Module Test");
    suite.addTest("test_returns_promise", test_returns_promise);
    suite.addTest("test_with_callback", test_with_callback);
    exit(suite.run());
}
