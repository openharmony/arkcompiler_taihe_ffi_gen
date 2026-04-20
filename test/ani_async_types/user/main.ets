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

async function assertAsyncError(task: () => Promise<Any>, expectedMessage?: string) {
    let promise = task();
    try {
        await promise;
        arktest.assertTrue(false, "Expected an error to be thrown, but promise resolved successfully");
    } catch (err) {
        if (expectedMessage) {
            arktest.assertTrue(err instanceof Error, "Expected an Error object");
            arktest.assertTrue(err.message.includes(expectedMessage), `Error message should include "${expectedMessage}", but got "${err.message}"`);
        }
    }
}

async function test_returns_promise() {
    let x = hello.futureResultReturnsPromise(1000, "InitialValue");
    console.log("Waiting for promise result...");
    await x.then((s: String) => {
        console.log("Promise Result: " + s);
        arktest.assertEQ("C++AsyncProcessed-InitialValue", s);
    });
}

async function test_with_callback() {
    let x = new Promise<string>((resolve, reject) => {
        hello.futureResultWithCallback(
            1000, "InitialValue",
            (err: BusinessError|null, res: String|undefined) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(res!);
                }
            });
    });
    console.log("Waiting for callback result...");
    await x.then((s: String) => {
        console.log("Callback Result: " + s);
        arktest.assertEQ("C++AsyncProcessed-InitialValue", s);
    });
}

function test_returns_promise_with_sync_error() {
    arktest.expectError(() => {
        hello.futureResultReturnsPromise(-1, "InitialValue");
    });
}

function test_with_callback_with_sync_error() {
    arktest.expectError(() => {
        hello.futureResultWithCallback(
            -1, "InitialValue",
            (err: BusinessError|null, res: String|undefined) => {
                // This callback should not be called due to sync error
            });
    });
}

async function test_returns_promise_with_async_error() {
    let x = hello.futureResultReturnsPromise(1000, "");
    console.log("Waiting for promise result with async error...");
    await assertAsyncError(() => x);
}

async function test_with_callback_with_async_error() {
    let x = new Promise<string>((resolve, reject) => {
        hello.futureResultWithCallback(
            1000, "", (err: BusinessError|null, res: String|undefined) => {
                console.log("Inside callback for async error test", err, res);
                if (err) {
                    reject(err);
                } else {
                    resolve(res!);
                }
            });
    });
    console.log("Waiting for callback result with async error...");
    await assertAsyncError(() => x);
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

async function test_reverse_returns_promise() {
    let user = new UserTypeImpl();
    let x = hello.processUserTypeReturnsPromise(user, 500, 500, "InitialValue");
    console.log("Waiting for promise result...");
    await x.then((s: String) => {
        console.log("Reverse Promise Result: " + s);
        arktest.assertEQ("C++AsyncProcessed-EtsAsyncProcessed-C++SyncProcessed-InitialValue", s);
    });
}

async function test_reverse_with_callback() {
    let user = new UserTypeImpl();
    let x = new Promise<string>((resolve, reject) => {
        hello.processUserTypeWithCallback(
            user, 500, 500, "InitialValue",
            (err: BusinessError|null, res: String|undefined) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(res!);
                }
            });
    });
    console.log("Waiting for callback result...");
    await x.then((s: String) => {
        console.log("Reverse Callback Result: " + s);
        arktest.assertEQ("C++AsyncProcessed-EtsAsyncProcessed-C++SyncProcessed-InitialValue", s);
    });
}

class SyncErrorUserTypeImpl implements hello.UserType {
    fooWithCallback(
        ms: long, result: string,
        set: (error: BusinessError|null, data: string|undefined) => void):
        void {
        throw new BusinessError(1, "Synchronous error in fooWithCallback");
    }
    fooReturnsPromise(ms: long, result: string): Promise<string> {
        throw new BusinessError(1, "Synchronous error in fooReturnsPromise");
    }
}

async function test_reverse_returns_promise_with_sync_error() {
    let user = new SyncErrorUserTypeImpl();
    let x = hello.processUserTypeReturnsPromise(user, 500, 500, "InitialValue");
    console.log("Waiting for promise result with sync error...");
    await assertAsyncError(() => x, "Synchronous error in fooReturnsPromise");
}

async function test_reverse_with_callback_with_sync_error() {
    let user = new SyncErrorUserTypeImpl();
    let x = new Promise<string>((resolve, reject) => {
        hello.processUserTypeWithCallback(
            user, 500, 500, "InitialValue",
            (err: BusinessError|null, res: String|undefined) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(res!);
                }
            });
    });
    console.log("Waiting for callback result with sync error...");
    await assertAsyncError(() => x, "Synchronous error in fooWithCallback");
}

class AsyncErrorUserTypeImpl implements hello.UserType {
    fooWithCallback(
        ms: long, result: string,
        set: (error: BusinessError|null, data: string|undefined) => void):
        void {
        setTimeout(() => {
            set(new BusinessError(1, "Asynchronous error in fooWithCallback"), undefined);
        }, ms.toInt());
    }
    fooReturnsPromise(ms: long, result: string): Promise<string> {
        return new Promise<string>((resolve, reject) => {
            setTimeout(() => {
                reject(new BusinessError(1, "Asynchronous error in fooReturnsPromise"));
            }, ms.toInt());
        });
    }
}

async function test_reverse_returns_promise_with_async_error() {
    let user = new AsyncErrorUserTypeImpl();
    let x = hello.processUserTypeReturnsPromise(user, 500, 500, "InitialValue");
    console.log("Waiting for promise result with async error...");
    await assertAsyncError(() => x, "Asynchronous error in fooReturnsPromise");
}

async function test_reverse_with_callback_with_async_error() {
    let user = new AsyncErrorUserTypeImpl();
    let x = new Promise<string>((resolve, reject) => {
        hello.processUserTypeWithCallback(
            user, 500, 500, "InitialValue",
            (err: BusinessError|null, res: String|undefined) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(res!);
                }
            });
    });
    console.log("Waiting for callback result with async error...");
    await assertAsyncError(() => x, "Asynchronous error in fooWithCallback");
}


function main() {
    const suite = new arktest.ArkTestsuite("Hello Module Test");

    suite.addAsyncTest("test_returns_promise", test_returns_promise);
    suite.addAsyncTest("test_with_callback", test_with_callback);
    suite.addTest("test_returns_promise_with_sync_error", test_returns_promise_with_sync_error);
    suite.addTest("test_with_callback_with_sync_error", test_with_callback_with_sync_error);
    suite.addAsyncTest("test_returns_promise_with_async_error", test_returns_promise_with_async_error);
    suite.addAsyncTest("test_with_callback_with_async_error", test_with_callback_with_async_error);

    suite.addAsyncTest("test_reverse_returns_promise", test_reverse_returns_promise);
    suite.addAsyncTest("test_reverse_with_callback", test_reverse_with_callback);
    suite.addAsyncTest("test_reverse_returns_promise_with_sync_error", test_reverse_returns_promise_with_sync_error);
    suite.addAsyncTest("test_reverse_with_callback_with_sync_error", test_reverse_with_callback_with_sync_error);
    suite.addAsyncTest("test_reverse_returns_promise_with_async_error", test_reverse_returns_promise_with_async_error);
    suite.addAsyncTest("test_reverse_with_callback_with_async_error", test_reverse_with_callback_with_async_error);

    exit(suite.run());
}
