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

const lib = requireNapi('./hello.so', RequireBaseDir.SCRIPT_DIR);

function testSayHello() {
    try {
        lib.sayHello();
        console.log('testSayHello Success');
    } catch (error) {
        if (error.toString() !== "Error: System initialization failed") {
            throw new Error(`Unexpected result`);
        }
        console.error('testSayHello Error caught:', error.toString());
    }
}

function testSayHelloWithNumber() {
    try {
        let result: number = lib.sayHello_ii(5);
        if (result !== 5) {
            throw new Error(`Unexpected result`);
        }
        console.log('testSayHelloWithNumber Success:', result);
    } catch (error) {
        console.error('testSayHelloWithNumber Error caught:', error.message, error.code);
    }
}

function testSayHelloWithError() {
    try {
        lib.sayHello_ii(10);
    } catch (error) {
        if (error.message !== "Index out of range" || error.code !== "10") {
            throw new Error(`Unexpected result`);
        }
        console.error('testSayHelloWithError Error caught:', error.message, error.code);
    }
}

function testFooBar() {
    try {
        let x = lib.createFoo();
        x.bar();
    } catch (error) {
        if (error.code !== "12" || error.message !== "A Error in bar") {
            throw new Error(`Unexpected result`);
        }
        console.error('testFooBar Error caught:', error.message, error.code);
    }
}

function testFooBarWithNumber() {
    try {
        let x = lib.createFoo();
        let result: number = x.bar_ii(20);
        if (result !== 21) {
            throw new Error(`Unexpected result`);
        }
        console.log('testFooBarWithNumber Success:', result);
    } catch (error) {
        console.error('testFooBarWithNumber Error caught:', error.message);
    }
}

function testCallFoo() {
    let x = lib.createFoo();
    try {
        const str = lib.callFoo(x);
    } catch (error) {
        console.error('testCallFoo Error caught:', error.message);
    }
}

function testCallback() {
    try {
        lib.callcb(() => {
            console.log("Callback called");
            throw Object.assign(new Error("Callback error"), { 
                code: 1001
            });
        });
    } catch (error) {
        if (error.code !== "1001" || error.message !== "Callback error") {
            throw new Error(`Unexpected result`);
        }
        console.error('testCallback Error caught:', error.message, error.code);
    }
}

function testCallbackWithReturn() {
    try {
        let result: number = 0;
        lib.callcb_ii((a: number) => {
            console.log("Callback_ii called", a);
            result = a;
            return a + 1;
        });
        if (result !== 1) {
            throw new Error(`Unexpected result`);
        }
        console.log('testCallbackWithReturn Success:', result);
    } catch (error) {
        console.error('testCallbackWithReturn Error caught:', error.message);
    }
}

function main() {
    console.log("=== Starting Hello Module Tests ===");
    
    testSayHello();
    testSayHelloWithNumber();
    testSayHelloWithError();
    testFooBar();
    testFooBarWithNumber();
    testCallFoo();
    testCallback();
    testCallbackWithReturn();
    
    console.log("=== All Hello Module Tests Completed ===");
}

main();