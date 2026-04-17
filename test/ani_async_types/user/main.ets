/*
 * Copyright (c) 2025-2026 Huawei Device Co., Ltd.
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

async function test_returns_promise(): Promise<void> {
    let x = hello.futureResultReturnsPromise(1000, "InitialValue");
    console.log("Waiting for result...");
    await x.then((s: String) => {
        console.log("Promise Result: " + s);
    });
}

async function test_with_callback(): Promise<void> {
    let x = new Promise<string>((resolve, reject) => {
        hello.futureResultWithCallback(
            1000, "InitialValue",
            (err: BusinessError|null, res: String|undefined) => {
                resolve(res!);
            });
    });
    console.log("Waiting for callback...");
    await x.then((s: String) => {
        console.log("Callback Result: " + s);
    });
}

class UserTypeImpl implements hello.UserType {
    fooWithCallback(
        ms: long, result: string,
        set: (error: BusinessError|null, data: string|undefined) => void):
        void {
        setTimeout(() => {
            set(null, "EtsAsyncProcessed-" + result);
        }, ms.toInt());
    }
    fooReturnsPromise(ms: long, result: string): Promise<string> {
        return new Promise<string>((resolve, reject) => {
            setTimeout(() => {
                resolve("EtsAsyncProcessed-" + result);
            }, ms.toInt());
        });
    }
}

async function test_reverse_with_callback(): Promise<void> {
    let user = new UserTypeImpl();
    let x = new Promise<string>((resolve, reject) => {
        hello.processUserTypeWithCallback(
            user, 500, 500, "InitialValue",
            (err: BusinessError|null, res: String|undefined) => {
                resolve(res!);
            });
    });
    console.log("Waiting for reverse callback...");
    await x.then((s: String) => {
        console.log("Reverse Callback Result: " + s);
    });
}

async function test_reverse_returns_promise(): Promise<void> {
    let user = new UserTypeImpl();
    let x = hello.processUserTypeReturnsPromise(user, 500, 500, "InitialValue");
    console.log("Waiting for reverse promise...");
    await x.then((s: String) => {
        console.log("Reverse Promise Result: " + s);
    });
}

function main(): void {
    const suite = new arktest.ArkTestsuite("Hello Module Test");
    suite.addAsyncTest("test_returns_promise", test_returns_promise);
    suite.addAsyncTest("test_with_callback", test_with_callback);
    suite.addAsyncTest("test_reverse_returns_promise", test_reverse_returns_promise);
    suite.addAsyncTest("test_reverse_with_callback", test_reverse_with_callback);
    exit(suite.run());
}
