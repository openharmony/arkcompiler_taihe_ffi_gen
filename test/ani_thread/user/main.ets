import * as threadTest from "@generated/thread_test";

loadLibrary("ani_thread");

function main() {
    threadTest.invokeFromOtherThreadAfter(1.0, () => {
        console.log("hello world");
    })
    // sleep 2 seconds to wait for the callback
    let start = Date.now();
    while (Date.now() - start < 2000) {
        // do nothing
    }
}
