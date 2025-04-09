import * as Test from "@generated/finalization_test";
import * as System from "std/core/System";

loadLibrary("ani_finalization");

function doFullGC() {
    try {
        GC.waitForFinishGC(GC.startGC(GC.FULL_CAUSE, GC.IN_PLACE_MODE));
    } catch (e) {
        assertTrue(false, "Unexpected exception during GC");
    }
}

function main() {
    console.log("begin")

    let foo: Test.Foo|null = Test.makeFoo();

    foo = null;

    doFullGC()
    Coroutine.Schedule()

    console.log("end")
}
