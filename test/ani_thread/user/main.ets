import {BusinessError} from "@ohos.base";
import * as threadTest from "thread_test";

loadLibrary("ani_thread");

function sleep(ms: int): Promise<void> {
    return new Promise<void>(resolve => { setTimeout(() => resolve(undefined), ms)});
}

function main() {
    threadTest.invokeFromOtherThreadAfter(1.0, () => {
        console.log("hello world");
    })
    await sleep(2000);
}
