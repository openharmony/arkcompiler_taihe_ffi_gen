/*
 * Copyright (c) 2026 Huawei Device Co., Ltd.
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

import * as test from "debug";

loadLibrary("ani_debug");

function testBadThrow() {
    test.testMayThrowCallback(() => {
        return;
    });
    test.testMayThrowCallback(() => {
        throw new Error("test error");
    });
    test.testNoThrowCallback(() => {
        return;
    });
    test.testNoThrowCallback(() => {
        throw new Error("test error");
    });  // should abort
}

function testBadAniToCpp1() {
    let array: Any = [new object(), new object()];
    test.testBadParam(array as Array<test.IntOrStr>);
}

function testBadAniToCpp2() {
    let callback: Any = () => {
        return new object();
    };
    test.testCallbackWithBadReturnType(callback as () => test.IntOrStr);
}

function testBadCppToAni() {
    test.testReturnBadEnum();
}

function testBadEnvGuard() {
    test.testBadEnvGuard();
}

function main() {
    // Uncomment the test you want to run

    // testBadThrow();
    // testBadAniToCpp1();
    // testBadAniToCpp2();
    // testBadCppToAni();
    // testBadEnvGuard();
}
