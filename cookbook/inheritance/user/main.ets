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
import * as lib from "class_extends";
import * as extends_inject from "extends_inject";

loadLibrary("inheritance");


function base_context_test() {
    let baseContext = lib.makeBaseContext();
    baseContext.name = "BaseContext";
    arktest.assertEQ(baseContext.name, "BaseContext");
    arktest.assertEQ(baseContext.getType("BCTX"), "BaseContextTypeBCTX");
}

function context_extends_test() {
    let context = lib.makeContext();
    context.stageMode = true;
    arktest.assertEQ(context.stageMode, true)
    arktest.assertEQ(context.name, "");
    context.name = "Context";
    arktest.assertEQ(context.name, "Context");
    context.getApplicationContext();
    arktest.assertEQ(context.getType("CTX"), "ContextTypeCTX");
}

function application_context_extends_test() {
    let applicationContext = lib.makeApplicationContext();
    applicationContext.setSupportedProcessCacheSync(true);
    applicationContext.setSupportedProcessCacheSync(false);
    applicationContext.setSupportedProcessCache(
        true, (error: BusinessError|null) => {
            if (error !== null && error.code !== 0) {
                console.log("call setSupportedProcessCache ERROR ", error);
            } else {
                console.log("call setSupportedProcessCache 333");
            }
        })
    applicationContext.setSupportedProcessCache(
        false, (error: BusinessError|null) => {
            if (error !== null && error.code !== 0) {
                console.log("call setSupportedProcessCache ERROR ", error);
            } else {
                console.log("call setSupportedProcessCache 333");
            }
        })
    applicationContext.name = "ApplicationContext";
    arktest.assertEQ(applicationContext.name, "ApplicationContext");
    arktest.assertEQ(applicationContext.stageMode, false)
    arktest.assertEQ(applicationContext.getType("ACTX"), "AppContextACTX");
}

function test_context_extends() {
    let testContext = lib.makeTestContext();
    testContext.getTestContext();
    arktest.assertEQ(testContext.getType("TCTX"), "TestContextTCTX");
    // error, getApplicationContext does not exist on type TestContext
    // testContext.getApplicationContext();
}

function extends_inject_test() {
    let man = new extends_inject.Man();
    let person = man.getPerson();
    arktest.assertEQ(person.name, "zhangsan");
    console.log(`person.name: ${person.name}`);
    let innerPerson = extends_inject.makePerson();
    console.log(`innerPerson: ${innerPerson}`);
}

function main() {
    console.log("##############start#############")
    const suite = new arktest.ArkTestsuite("class extends ut")

    suite.addTest("base context test", base_context_test)
    suite.addTest("context extends test", context_extends_test)
    suite.addTest(
        "application context extends test", application_context_extends_test)
    suite.addTest("test context extends", test_context_extends)
    suite.addTest("extends inject test", extends_inject_test)
    exit(suite.run())
}
