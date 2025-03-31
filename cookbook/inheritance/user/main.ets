import * as lib from "@generated/class_extends";
import * as extends_inject from "@generated/extends_inject";
import * as System from "std/core/System";

loadLibrary("inheritance");


function base_context_test() {
    let baseContext = lib.makeBaseContext();
    baseContext.name = "BaseContext";
    assertEQ(baseContext.name, "BaseContext");
    assertEQ(baseContext.getType("BCTX"), "BaseContextTypeBCTX");
}

function context_extends_test() {
    let context = lib.makeContext();
    context.stageMode = true;
    assertEQ(context.stageMode, true)
    assertEQ(context.name, "");
    context.name = "Context";
    assertEQ(context.name, "Context");
    context.getApplicationContext();
    assertEQ(context.getType("CTX"), "ContextTypeCTX");
}

function application_context_extends_test() {
    let applicationContext = lib.makeApplicationContext();
    applicationContext.setSupportedProcessCacheSync(true);
    applicationContext.setSupportedProcessCacheSync(false);
    applicationContext.setSupportedProcessCache(true, (error: Error) => {
        if (!error.message) {
            console.log("call setSupportedProcessCache 333");
        } else {
            console.log("call setSupportedProcessCache ERROR ", error);
        }
    })
    applicationContext.setSupportedProcessCache(false, (error: Error) => {
        if (!error.message) {
            console.log("call setSupportedProcessCache 333");
        } else {
            console.log("call setSupportedProcessCache ERROR ", error);
        }
    })
    applicationContext.name = "ApplicationContext";
    assertEQ(applicationContext.name, "ApplicationContext");
    assertEQ(applicationContext.stageMode, false)
    assertEQ(applicationContext.getType("ACTX"), "AppContextACTX");
}

function test_context_extends() {
    let testContext = lib.makeTestContext();
    testContext.getTestContext();
    assertEQ(testContext.getType("TCTX"), "TestContextTCTX");
    // error, getApplicationContext does not exist on type TestContext
    // testContext.getApplicationContext();
}

function extends_inject_test() {
    let man = new extends_inject.Man();
    let person = man.getPerson();
    assertEQ(person.name, "zhangsan");
    console.log(`person.name: ${person.name}`);
    let innerPerson = extends_inject.makePerson();
    console.log(`innerPerson: ${innerPerson}`);
}

function main() {
    console.log("##############start#############")
    const suite = new ArkTestsuite("class extends ut")

    suite.addTest("base context test", base_context_test)
    suite.addTest("context extends test", context_extends_test)
    suite.addTest(
        "application context extends test", application_context_extends_test)
    suite.addTest("test context extends", test_context_extends)
    suite.addTest("extends inject test", extends_inject_test)
    System.exit(suite.run())
}
