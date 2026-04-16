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
    let x = hello.futureResultReturnsPromise(1000, "InitialValue");
    console.log("Waiting for result...");
    waitForCompletion(() => x.then((s: String) => {
        console.log("Promise Result: " + s);
    }));
}

function test_with_callback(): void {
    let x = new Promise<string>((resolve, reject) => {
        hello.futureResultWithCallback(
            1000, "InitialValue",
            (err: BusinessError|null, res: String|undefined) => {
                resolve(res!);
            });
    });
    console.log("Waiting for callback...");
    waitForCompletion(() => x.then((s: String) => {
        console.log("Callback Result: " + s);
    }));
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

function test_reverse_with_callback(): void {
    let user = new UserTypeImpl();
    let x = new Promise<string>((resolve, reject) => {
        hello.processUserTypeWithCallback(
            user, 500, 500, "InitialValue",
            (err: BusinessError|null, res: String|undefined) => {
                resolve(res!);
            });
    });
    console.log("Waiting for reverse callback...");
    waitForCompletion(() => x.then((s: String) => {
        console.log("Reverse Callback Result: " + s);
    }));
}

function test_reverse_returns_promise(): void {
    let user = new UserTypeImpl();
    let x = hello.processUserTypeReturnsPromise(user, 500, 500, "InitialValue");
    console.log("Waiting for reverse promise...");
    waitForCompletion(() => x.then((s: String) => {
        console.log("Reverse Promise Result: " + s);
    }));
}

function main(): void {
    const suite = new arktest.ArkTestsuite("Hello Module Test");
    suite.addTest("test_returns_promise", test_returns_promise);
    suite.addTest("test_with_callback", test_with_callback);
    suite.addTest("test_reverse_returns_promise", test_reverse_returns_promise);
    suite.addTest("test_reverse_with_callback", test_reverse_with_callback);
    exit(suite.run());
}
