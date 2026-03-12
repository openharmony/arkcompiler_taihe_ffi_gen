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

import * as test from "test";

loadLibrary("ani_consistency");

class MyObjectImpl implements test.MyObject {
    invoke() {
        console.log("MyObjectImpl::invoke() called");
    }
}

function testObjectConsistency() {
    const container = test.createObjectContainer();
    const obj = new MyObjectImpl();
    container.save(obj);
    const takenObj = container.take();
    arktest.assertEQ(obj, takenObj);
}

function testCallbackConsistency() {
    const container = test.createCallbackContainer();
    const callback = (s: String) => console.log("Callback called with: " + s);
    container.save(callback);
    const takenCallback = container.take();
    arktest.assertEQ(callback, takenCallback);
}

function main() {
    const suite = new arktest.ArkTestsuite("Consistency Tests");

    suite.addTest("Object Identity Test", testObjectConsistency);
    suite.addTest("Callback Identity Test", testCallbackConsistency);

    exit(suite.run())
}
