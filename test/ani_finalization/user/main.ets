import {BusinessError} from "@ohos.base";
import * as Test from "finalization_test";

loadLibrary("ani_finalization");

function doFullGC() {
    try {
        GC.waitForFinishGC(GC.startGC(GC.Cause.FULL, GC.IN_PLACE_MODE));
    } catch (e) {
        arktest.assertTrue(false, "Unexpected exception during GC");
    }
}

function test_finalization() {
    let flag: int = 0;

    let foo: Test.Foo|null = new Test.Foo();

    foo.addCallback(() => {
        console.log("Bye!");
    })

    console.log("Doing full GC before setting foo to null...");
    doFullGC()
    Coroutine.Schedule()

    foo.addCallback(() => {
        flag = 42;
    })

    foo = null;

    console.log("Doing full GC after setting foo to null...");
    doFullGC()
    Coroutine.Schedule()

    arktest.assertEQ(flag, 42);
}

function main() {
    console.log("begin")

    const suite = new arktest.ArkTestsuite("FuncTest Test");

    suite.addTest("test finalization", test_finalization);

    exit(suite.run());
}
