import {BusinessError} from "@ohos.base";
import * as async_test from "async";

loadLibrary("async");
function main() {
    console.log("addSync: ", async_test.addSync(1, 2))

    async_test.add(10, 20, (error: BusinessError|null, data?: int) => {
        if (error !== null && error.code !== 0) {
            console.log("async ERROR ", error);
        } else {
            console.log("async success ", data);
        }
    })

    try {
        let retPromise = await async_test.add(0, 2);
        console.log("async promise success ")
    } catch (error) {
        console.error("async promise ERROR ", error)
    }


    // async interface method example
    let istringholder = async_test.makeIStringHolder();
    console.log(istringholder.newGet());

    istringholder.set("interface async set", (error: BusinessError|null) => {
        if (error !== null && error.code !== 0) {
            console.log("interface async ERROR ", error);
        } else {
            console.log("interface async success ");
        }
    })

    let p_istringholder = istringholder.getPromise();
    p_istringholder
        .then((ret: Any) => {
            let retInner = ret as string;
            console.log("interface async success p_istringholder ", retInner)
        })
        .catch((ret: Any) => {
            let retError = ret as Error;
            console.error(
                "interface async promise ERROR p_istringholder ", retError)
        });

    CoroutineExtras.stopTaskpool();
}