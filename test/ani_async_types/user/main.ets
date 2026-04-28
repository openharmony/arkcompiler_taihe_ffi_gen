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

type AsyncCallback<T> = (error: BusinessError|null, data: T|undefined) => void;

async function assertAsyncError(
    task: () => Promise<Any>, expectedMessage?: string) {
    let promise = task();
    try {
        await promise;
        arktest.assertTrue(
            false,
            "Expected an error to be thrown, but promise resolved successfully");
    } catch (err) {
        if (expectedMessage) {
            arktest.assertTrue(
                err instanceof Error, "Expected an Error object");
            arktest.assertTrue(
                err.message.includes(expectedMessage),
                `Error message should include "${expectedMessage}", but got "${
                    err.message}"`);
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
    fooWithCallback(ms: long, result: string, set: AsyncCallback<string>):
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
        arktest.assertEQ(
            "C++AsyncProcessed-EtsAsyncProcessed-C++SyncProcessed-InitialValue",
            s);
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
        arktest.assertEQ(
            "C++AsyncProcessed-EtsAsyncProcessed-C++SyncProcessed-InitialValue",
            s);
    });
}

class SyncErrorUserTypeImpl implements hello.UserType {
    fooWithCallback(ms: long, result: string, set: AsyncCallback<string>):
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
    fooWithCallback(ms: long, result: string, set: AsyncCallback<string>):
        void {
        setTimeout(() => {
            set(new BusinessError(1, "Asynchronous error in fooWithCallback"),
                undefined);
        }, ms.toInt());
    }
    fooReturnsPromise(ms: long, result: string): Promise<string> {
        return new Promise<string>((resolve, reject) => {
            setTimeout(() => {
                reject(new BusinessError(
                    1, "Asynchronous error in fooReturnsPromise"));
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

class VoidAsyncUserTypeImpl implements hello.VoidAsyncUserType {
    barWithCallback(set: AsyncCallback<void>): void {
        setTimeout(() => {
            set(null, undefined);
        }, 100);
    }
    barReturnsPromise(): Promise<void> {
        return new Promise<void>((resolve, reject) => {
            setTimeout(() => {
                resolve(undefined);
            }, 100);
        });
    }
}

async function test_void_async_with_callback() {
    let x = new Promise<void>((resolve, reject) => {
        hello.testVoidAsyncWithCallback(100, (err: BusinessError|null) => {
            if (err) {
                reject(err);
            } else {
                resolve(undefined);
            }
        });
    });
    await x;
    arktest.assertTrue(true);
}

async function test_void_async_returns_promise() {
    await hello.testVoidAsyncReturnsPromise(100);
    arktest.assertTrue(true);
}

async function test_reverse_void_async_with_callback() {
    let user = new VoidAsyncUserTypeImpl();
    let x = new Promise<void>((resolve, reject) => {
        hello.testReverseVoidAsyncWithCallback(
            user, (err: BusinessError|null) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(undefined);
                }
            });
    });
    await x;
    arktest.assertTrue(true);
}

async function test_reverse_void_async_returns_promise() {
    let user = new VoidAsyncUserTypeImpl();
    await hello.testReverseVoidAsyncReturnsPromise(user);
    arktest.assertTrue(true);
}

class SyncBoolUserTypeImpl implements hello.SyncOrAsyncUserType {
    baz(): hello.syncOrAsyncBool {
        return true;
    }
}

class AsyncBoolUserTypeImpl implements hello.SyncOrAsyncUserType {
    baz(): hello.syncOrAsyncBool {
        return new Promise<boolean>((resolve, reject) => {
            setTimeout(() => {
                resolve(false);
            }, 100);
        });
    }
}

async function test_sync_or_async_with_sync_value() {
    let result = await hello.testSyncOrAsync(new SyncBoolUserTypeImpl());
    arktest.assertEQ("C++SyncBool-true", result);
}

async function test_sync_or_async_with_async_value() {
    let result = await hello.testSyncOrAsync(new AsyncBoolUserTypeImpl());
    arktest.assertEQ("C++AsyncBool-false", result);
}

async function test_double_async_results() {
    let result = hello.getDoubleAsyncResults("First", (21).toLong());
    arktest.assertEQ("C++AsyncProcessed-First", await result.first);
    arktest.assertEQ((42).toLong(), await result.second);
}

async function test_many_async_results() {
    let result =
        await Promise.all(hello.getManyAsyncResults((3).toLong(), "Batch"));
    arktest.assertEQ(3, result.length);
    arktest.assertEQ("C++AsyncProcessed-Batch-0", result[0]);
    arktest.assertEQ("C++AsyncProcessed-Batch-1", result[1]);
    arktest.assertEQ("C++AsyncProcessed-Batch-2", result[2]);
}

async function test_complex_async_result() {
    let result =
        await hello.getComplexAsyncResult("Complex", (7).toLong(), true);
    arktest.assertEQ("Complex", result.str);
    arktest.assertEQ((7).toLong(), result.num);
    arktest.assertEQ(true, result.flag);
}

async function test_string_or_number_string() {
    let result =
        await hello.getStringOrNumber(true, "StringValue", (9).toLong());
    arktest.assertEQ("StringValue", result);
}

async function test_string_or_number_number() {
    let result =
        await hello.getStringOrNumber(false, "StringValue", (9).toLong());
    arktest.assertEQ((9).toLong(), result);
}

async function test_container() {
    let result = await hello.getContainer();
    arktest.assertEQ(3, result.length);
    arktest.assertEQ("alpha", result[0]);
    arktest.assertEQ("beta", result[1]);
    arktest.assertEQ("gamma", result[2]);
}

async function test_nested_future() {
    let outer = await hello.getNestedFuture();
    let value = await outer;
    arktest.assertEQ("C++NestedFuture", value);
}

function main() {
    const suite = new arktest.ArkTestsuite("Hello Module Test");

    suite.addAsyncTest("test_returns_promise", test_returns_promise);
    suite.addAsyncTest("test_with_callback", test_with_callback);
    suite.addTest(
        "test_returns_promise_with_sync_error",
        test_returns_promise_with_sync_error);
    suite.addTest(
        "test_with_callback_with_sync_error",
        test_with_callback_with_sync_error);
    suite.addAsyncTest(
        "test_returns_promise_with_async_error",
        test_returns_promise_with_async_error);
    suite.addAsyncTest(
        "test_with_callback_with_async_error",
        test_with_callback_with_async_error);

    suite.addAsyncTest(
        "test_reverse_returns_promise", test_reverse_returns_promise);
    suite.addAsyncTest(
        "test_reverse_with_callback", test_reverse_with_callback);
    suite.addAsyncTest(
        "test_reverse_returns_promise_with_sync_error",
        test_reverse_returns_promise_with_sync_error);
    suite.addAsyncTest(
        "test_reverse_with_callback_with_sync_error",
        test_reverse_with_callback_with_sync_error);
    suite.addAsyncTest(
        "test_reverse_returns_promise_with_async_error",
        test_reverse_returns_promise_with_async_error);
    suite.addAsyncTest(
        "test_reverse_with_callback_with_async_error",
        test_reverse_with_callback_with_async_error);
    suite.addAsyncTest(
        "test_void_async_with_callback", test_void_async_with_callback);
    suite.addAsyncTest(
        "test_void_async_returns_promise", test_void_async_returns_promise);
    suite.addAsyncTest(
        "test_reverse_void_async_with_callback",
        test_reverse_void_async_with_callback);
    suite.addAsyncTest(
        "test_reverse_void_async_returns_promise",
        test_reverse_void_async_returns_promise);
    suite.addAsyncTest(
        "test_sync_or_async_with_sync_value",
        test_sync_or_async_with_sync_value);
    suite.addAsyncTest(
        "test_sync_or_async_with_async_value",
        test_sync_or_async_with_async_value);
    suite.addAsyncTest("test_double_async_results", test_double_async_results);
    suite.addAsyncTest("test_many_async_results", test_many_async_results);
    suite.addAsyncTest("test_complex_async_result", test_complex_async_result);
    suite.addAsyncTest(
        "test_string_or_number_string", test_string_or_number_string);
    suite.addAsyncTest(
        "test_string_or_number_number", test_string_or_number_number);
    suite.addAsyncTest("test_container", test_container);
    suite.addAsyncTest("test_nested_future", test_nested_future);

    exit(suite.run());
}
