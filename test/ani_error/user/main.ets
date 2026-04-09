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

// ==================== 全局函数测试 ====================

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

function testCallback() {
    let result: int = 0;
    try {
        result = hello.callcb(() => {
            console.log("Callback called");
            throw new BusinessError(1001, new Error("Callback error"));
        });
    } catch (error) {
        console.log("Error in testCallback")
    }
    arktest.assertEQ(100, result);
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

function testCallbackVoid() {
    try {
        hello.test_cb_v(() => {
            console.log("test_cb_v in ets");
        });
    } catch (error) {
        console.log("Error in testCallbackVoid")
    }
}

function testSayHelloParam() {
    try {
        hello.sayHelloParam(100);
    } catch (error) {
        console.log("Error in testSayHelloParam")
    }
}

function testSayHelloReturn() {
    let result: int = 0;
    try {
        result = hello.sayHelloReturn();
    } catch (error) {
        console.log("Error in testSayHelloReturn")
    }
    arktest.assertEQ(123, result);
}

function testProcessGlobalNoexceptCallback() {
    let result: int = 0;
    try {
        result = hello.processGlobalNoexceptCallback((a: int) => {
            console.log("processGlobalNoexceptCallback called with:", a);
            return a * 3;
        });
    } catch (error) {
        console.log("Error in testProcessGlobalNoexceptCallback")
    }
    arktest.assertEQ(600, result);
}

function testProcessGlobalVoidCallback() {
    let called: boolean = false;
    try {
        hello.processGlobalVoidCallback(() => {
            console.log("processGlobalVoidCallback called");
            called = true;
        });
    } catch (error) {
        console.log("Error in testProcessGlobalVoidCallback")
    }
    arktest.assertEQ(true, called);
}

function testProcessGlobalVoidNoexceptCallback() {
    let called: boolean = false;
    try {
        hello.processGlobalVoidNoexceptCallback(() => {
            console.log("processGlobalVoidNoexceptCallback called");
            called = true;
        });
    } catch (error) {
        console.log("Error in testProcessGlobalVoidNoexceptCallback")
    }
    arktest.assertEQ(true, called);
}

function testProcessGlobalReturnNoexceptCallback() {
    let result: int = 0;
    try {
        result = hello.processGlobalReturnNoexceptCallback();
    } catch (error) {
        console.log("Error in testProcessGlobalReturnNoexceptCallback")
    }
    arktest.assertEQ(111, result);
}

function testProcessGlobalNoexceptNoParamNoReturn() {
    try {
        hello.processGlobalNoexceptNoParamNoReturn();
    } catch (error) {
        console.log("Error in testProcessGlobalNoexceptNoParamNoReturn")
    }
}

function testProcessGlobalNoexceptParamNoReturn() {
    try {
        hello.processGlobalNoexceptParamNoReturn(500);
    } catch (error) {
        console.log("Error in testProcessGlobalNoexceptParamNoReturn")
    }
}

function testProcessGlobalNoexceptParamReturn() {
    let result: int = 0;
    try {
        result = hello.processGlobalNoexceptParamReturn(250);
    } catch (error) {
        console.log("Error in testProcessGlobalNoexceptParamReturn")
    }
    arktest.assertEQ(500, result);
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
    try {
        x.bar_iv(789);
    } catch (error) {
        console.log("Error in testFooBarWithString")
    }
}

function testFooBarReturn() {
    let x = hello.createFoo();
    let result: int = 0;
    try {
        result = x.bar_vi();
    } catch (error) {
        console.log("Error in testFooBarReturn")
    }
    arktest.assertEQ(123, result);
}

function testFooTestBar() {
    let x = hello.createFoo();
    try {
        x.test_bar();
    } catch (error) {
        console.log("Error in testFooTestBar")
    }
}

function testFooTestBarWithNumber() {
    let x = hello.createFoo();
    let result: int = 0;
    try {
        result = x.test_bar_ii(20);
    } catch (error) {
        console.log("Error in testFooTestBarWithNumber")
    }
    arktest.assertEQ(40, result);
}

function testFooTestBarWithString() {
    let x = hello.createFoo();
    try {
        x.test_bar_iv(789);
    } catch (error) {
        console.log("Error in testFooTestBarWithString")
    }
}

function testFooTestBarReturn() {
    let x = hello.createFoo();
    let result: int = 0;
    try {
        result = x.test_bar_vi();
    } catch (error) {
        console.log("Error in testFooTestBarReturn")
    }
    arktest.assertEQ(456, result);
}

function testFooCallcb() {
    let x = hello.createFoo();
    let result: int = 0;
    try {
        result = x.callcb(() => {
            console.log("Foo callcb called");
            throw new BusinessError(1002, new Error("Foo callcb error"));
        });
    } catch (error) {
        console.log("Error in testFooCallcb")
    }
    arktest.assertEQ(100, result);
}

function testFooCallcbWithReturn() {
    let x = hello.createFoo();
    let result: int = 0;
    try {
        result = x.callcb_ii((a: int) => {
            console.log("Foo callcb_ii called", a);
            return a + 1;
        });
    } catch (error) {
        console.log("Error in testFooCallcbWithReturn")
    }
    arktest.assertEQ(2, result);
}

function testFooTestCbV() {
    let x = hello.createFoo();
    try {
        x.test_cb_v(() => {
            console.log("Foo test_cb_v in ets");
        });
    } catch (error) {
        console.log("Error in testFooTestCbV")
    }
}

function testFooTestCbVWithReturn() {
    let x = hello.createFoo();
    let result: int = 0;
    try {
        result = x.test_cb_ii((a: int) => {
            console.log("Foo test_cb_ii called", a);
            return a + 1;
        });
    } catch (error) {
        console.log("Error in testFooTestCbVWithReturn")
    }
    arktest.assertEQ(101, result);
}

function testCallFoo() {
    let x = hello.createFoo();
    const str = hello.callFoo(x);
    arktest.assertEQ("A Error in bar", str);
}

function main() {
    // ==================== 全局函数测试 ====================
    printSection("=== 全局函数测试 ===");

    // 普通函数（可能抛出错误）
    testSayHello();
    testSayHelloWithNumber();
    testSayHelloWithError();
    testSayHelloParam();

    // 普通回调函数
    testCallback();
    testCallbackWithReturn();
    testCallbackVoid();

    // 全局函数：以普通 callback 作为参数
    testProcessGlobalVoidCallback();
    testProcessGlobalVoidNoexceptCallback();
    testProcessGlobalReturnNoexceptCallback();

    // 全局函数：noexcept，无 callback 参数
    testProcessGlobalNoexceptNoParamNoReturn();
    testProcessGlobalNoexceptParamNoReturn();
    testProcessGlobalNoexceptParamReturn();

    // ==================== 接口方法测试 ====================
    printSection("=== 接口方法测试 ===");

    // 普通接口方法（可能抛出错误）
    testFooBar();
    testFooBarWithNumber();
    testFooBarWithString();
    testFooBarReturn();

    // noexcept 接口方法
    testFooTestBar();
    testFooTestBarWithNumber();
    testFooTestBarWithString();
    testFooTestBarReturn();

    // 接口方法：以普通 callback 作为参数
    testFooCallcb();
    testFooCallcbWithReturn();
    testFooTestCbV();
    testFooTestCbVWithReturn();

    testCallFoo();
}

function printSection(title: string) {
    console.log("\n" + title);
}
