import * as Test from "@generated/finalization_test";
import {BusinessError} from "@ohos.base";

loadLibrary("ani_finalization");

function doFullGC() {
    try {
        GC.waitForFinishGC(GC.startGC(GC.Cause.FULL, GC.IN_PLACE_MODE));
    } catch (e) {
        assertTrue(false, "Unexpected exception during GC");
    }
}

function test_finalization() {
    let flag: int = 0;

    let foo: Test.Foo|null = Test.makeFoo();
    foo.addCallback(() => {
        flag = 42;
    })
    foo.addCallback(() => {
        console.log("Bye!");
    })
    foo = null;

    console.log("...")

    doFullGC()
    Coroutine.Schedule()

    assertEQ(flag, 42);
}

function main() {
    console.log("begin")

    const suite = new ArkTestsuite("FuncTest Test");

    suite.addTest("test finalization", test_finalization);

    exit(suite.run());
}
