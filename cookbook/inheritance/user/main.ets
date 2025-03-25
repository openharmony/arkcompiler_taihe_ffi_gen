import ApplicationContext from "../author_generated/class_extends";
import {BaseContext, Context, TestContext} from "../author_generated/class_extends";
import * as extends_inject from "../author_generated/extends_inject"
import {Man} from "../author_generated/extends_inject";

loadLibrary("inheritance")


function base_context_test() {
    let baseContext = new BaseContext();
    baseContext.setName("BaseContext");
    assertEQ(baseContext.getName(), "BaseContext");
    assertEQ(baseContext.getType("BCTX"), "BaseContextTypeBCTX");
}

function context_extends_test() {
    let context = new Context();
    context.stageMode = true;
    assertEQ(context.stageMode, true)
    assertEQ(context.getName(), "");
    context.setName("Context");
    assertEQ(context.getName(), "Context");
    context.getApplicationContext();
    assertEQ(context.getType("CTX"), "ContextTypeCTX");
}

function application_context_extends_test() {
    let applicationContext = new ApplicationContext();
    applicationContext.setSupportedProcessCacheSync(true);
    applicationContext.setSupportedProcessCacheSync(false);
    applicationContext.setSupportedProcessCache(true);
    applicationContext.setSupportedProcessCache(false);
    applicationContext.setName("ApplicationContext");
    assertEQ(applicationContext.getName(), "ApplicationContext");
    assertEQ(applicationContext.stageMode, false)
    assertEQ(applicationContext.getType("ACTX"), "AppContextACTX");
}

function test_context_extends() {
    let testContext = new TestContext();
    testContext.getTestContext();
    assertEQ(testContext.getType("TCTX"), "TestContextTCTX");
    // error, getApplicationContext does not exist on type TestContext
    // testContext.getApplicationContext();
}

function extends_inject_test() {
    let man = new Man();
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
    suite.run()
}
