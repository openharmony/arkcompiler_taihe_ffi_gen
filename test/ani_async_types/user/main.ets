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
                if (err) {
                    reject(err);
                } else {
                    resolve(res!);
                }
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
                if (err) {
                    reject(err);
                } else {
                    resolve(res!);
                }
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

function test_returns_promise_error_sync(): void {
    let err: BusinessError|undefined;
    try {
        let x = hello.futureResultReturnsPromise(-1, "InitialValue");
        waitForCompletion(() => x.then((s: String) => {
            console.log("Promise Result (unexpected success): " + s);
        }));
    } catch (e) {
        err = e as BusinessError;
    }
    arktest.assertNE(
        err, undefined,
        "futureResultReturnsPromise should throw on negative ms");
    arktest.assertEQ(
        err?.message, "ms cannot be negative", "error message should match");
}

function test_returns_promise_error_async(): void {
    let err: BusinessError|undefined;
    try {
        let x = hello.futureResultReturnsPromise(100, "");
        waitForCompletion(() => x.then((s: String) => {
            console.log("Promise Result (unexpected success): " + s);
        }));
    } catch (e) {
        err = e as BusinessError;
    }
    arktest.assertNE(
        err, undefined,
        "futureResultReturnsPromise should reject on empty result");
    arktest.assertEQ(
        err?.message, "val cannot be empty", "error message should match");
}

function test_with_callback_error_sync(): void {
    let err: BusinessError|undefined;
    let x = new Promise<string>((resolve, reject) => {
        hello.futureResultWithCallback(
            -1, "InitialValue",
            (err: BusinessError|null, res: String|undefined) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(res!);
                }
            });
    });
    try {
        waitForCompletion(() => x.then((s: String) => {
            console.log("Callback Result (unexpected success): " + s);
        }));
    } catch (e) {
        err = e as BusinessError;
    }
    arktest.assertNE(
        err, undefined, "futureResultWithCallback should throw on negative ms");
    arktest.assertEQ(
        err?.message, "ms cannot be negative", "error message should match");
}

function test_with_callback_error_async(): void {
    let err: BusinessError|undefined;
    let x = new Promise<string>((resolve, reject) => {
        hello.futureResultWithCallback(
            100, "", (err: BusinessError|null, res: String|undefined) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(res!);
                }
            });
    });
    try {
        waitForCompletion(() => x.then((s: String) => {
            console.log("Callback Result (unexpected success): " + s);
        }));
    } catch (e) {
        err = e as BusinessError;
    }
    arktest.assertNE(
        err, undefined,
        "futureResultWithCallback should reject on empty result");
    arktest.assertEQ(
        err?.message, "val cannot be empty", "error message should match");
}

function test_reverse_with_callback_error(): void {
    let err: BusinessError|undefined;
    let user = new UserTypeImpl();
    let x = new Promise<string>((resolve, reject) => {
        hello.processUserTypeWithCallback(
            user, -1, 500, "InitialValue",
            (err: BusinessError|null, res: String|undefined) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(res!);
                }
            });
    });
    try {
        waitForCompletion(() => x.then((s: String) => {
            console.log("Reverse Callback Result (unexpected success): " + s);
        }));
    } catch (e) {
        err = e as BusinessError;
    }
    arktest.assertNE(
        err, undefined,
        "processUserTypeWithCallback should throw on negative etsMs");
    arktest.assertEQ(
        err?.message, "ms cannot be negative", "error message should match");
}

function test_reverse_returns_promise_error(): void {
    let err: BusinessError|undefined;
    let user = new UserTypeImpl();
    try {
        let x =
            hello.processUserTypeReturnsPromise(user, 500, -1, "InitialValue");
        waitForCompletion(() => x.then((s: String) => {
            console.log("Reverse Promise Result (unexpected success): " + s);
        }));
    } catch (e) {
        err = e as BusinessError;
    }
    arktest.assertNE(
        err, undefined,
        "processUserTypeReturnsPromise should throw on negative cppMs");
    arktest.assertEQ(
        err?.message, "ms cannot be negative", "error message should match");
}

function main() {
    const suite = new arktest.ArkTestsuite("Hello Module Test");
    suite.addTest("test_returns_promise", test_returns_promise);
    suite.addTest("test_with_callback", test_with_callback);
    suite.addTest("test_reverse_returns_promise", test_reverse_returns_promise);
    suite.addTest("test_reverse_with_callback", test_reverse_with_callback);
    suite.addTest(
        "test_returns_promise_error_sync", test_returns_promise_error_sync);
    suite.addTest(
        "test_returns_promise_error_async", test_returns_promise_error_async);
    suite.addTest(
        "test_with_callback_error_sync", test_with_callback_error_sync);
    suite.addTest(
        "test_with_callback_error_async", test_with_callback_error_async);
    suite.addTest(
        "test_reverse_with_callback_error", test_reverse_with_callback_error);
    suite.addTest(
        "test_reverse_returns_promise_error",
        test_reverse_returns_promise_error);
    exit(suite.run());
}
