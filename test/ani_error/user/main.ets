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

loadLibrary("ani_error");

function testSayHello() {
    let errorMsg: string = "";
    try {
        hello.sayHello();
    } catch (error) {
        errorMsg = error.toString();
    }
    arktest.assertEQ("Error: System initialization failed", errorMsg);
}

function testSayHelloWithNumber() {
    let result: int = 0;
    try {
        result = hello.sayHello_ii(5);
    } catch (error) {
        console.log("Error in testSayHelloWithNumber")
    }
    arktest.assertEQ(5, result);
}

function testSayHelloWithError() {
    let error_code: number = 0;
    let errorMsg: string = "";
    try {
        hello.sayHello_ii(10);
    } catch (error) {
        errorMsg = error.toString();
        error = error as BusinessError
        error_code = error.code
    }
    arktest.assertEQ(error_code, 10);
    arktest.assertEQ("Error: Index out of range", errorMsg);
}

function testFooBar() {
    let x = hello.createFoo();
    let error_code: number = 0;
    let errorMsg: string = "";
    try {
        x.bar();
    } catch (error) {
        errorMsg = error.toString();
        error = error as BusinessError
        error_code = error.code
    }
    arktest.assertEQ(error_code, 12);
    arktest.assertEQ("Error: A Error in bar", errorMsg);
}

function testFooBarWithNumber() {
    let x = hello.createFoo();
    let result: int = 0;
    try {
        result = x.bar_ii(20);
    } catch (error) {
        console.log("Error in testFooBarWithNumber")
    }
    arktest.assertEQ(21, result);
}

function testFooBarWithString() {
    let x = hello.createFoo();
    let result: string = "";
    try {
        result = x.bar_ss("call_foo_bar_string");
    } catch (error) {
        console.log("Error in testFooBarWithString")
    }
    arktest.assertEQ("call_foo_bar_string_cpp", result);
}

function testCallFoo() {
    let x = hello.createFoo();
    const str = hello.callFoo(x);
    arktest.assertEQ("A Error in bar", str);
}

function testCallback() {
    let error_code: number = 0;
    let errorMsg: string = "";
    try {
        hello.callcb(() => {
            console.log("Callback called");
            throw new BusinessError(1001, new Error("Callback error"));
        });
    } catch (error) {
        errorMsg = error.toString();
        error = error as BusinessError
        error_code = error.code
    }
    arktest.assertEQ(error_code, 1001);
    arktest.assertEQ("Error: Callback error", errorMsg);
}

function testCallbackWithReturn() {
    let result: int = 0;
    try {
        hello.callcb_ii((a: int) => {
            console.log("Callback_ii called", a);
            result = a;
            return a + 1;
        });
    } catch (error) {
        console.log("Error in testCallbackWithReturn")
    }
    arktest.assertEQ(1, result);
}

function testConcat() {
    let res: string = "";
    try {
        res = hello.concat("a", "b");
    } catch (error) {
        console.log("Error in testConcat")
    }
    arktest.assertEQ("ab", res);
}

function testCallbackVoid() {
    try {
        hello.test_cb_v(() => {
            console.log("test_cb_v in ets");
        });
    } catch (error) {
        console.log("Error in testCallbackVoid")
    }
}

function main() {
    const suite = new arktest.ArkTestsuite("Hello Module Test");
    suite.addTest("testSayHello", testSayHello);
    suite.addTest("testSayHelloWithNumber", testSayHelloWithNumber);
    suite.addTest("testSayHelloWithError", testSayHelloWithError);
    suite.addTest("testFooBar", testFooBar);
    suite.addTest("testFooBarWithNumber", testFooBarWithNumber);
    suite.addTest("testFooBarWithString", testFooBarWithString);
    suite.addTest("testCallFoo", testCallFoo);
    suite.addTest("testCallback", testCallback);
    suite.addTest("testCallbackWithReturn", testCallbackWithReturn);
    suite.addTest("testConcat", testConcat);
    suite.addTest("testCallbackVoid", testCallbackVoid);
    exit(suite.run());
}
