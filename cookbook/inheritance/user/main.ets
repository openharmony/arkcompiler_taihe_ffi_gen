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
