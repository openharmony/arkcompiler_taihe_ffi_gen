import * as async_test from "@generated/async";

loadLibrary("async");
function main() {
    console.log("addSync: ", async_test.addSync(1, 2))

    async_test.add(10, 20, (error: Error, data?: int) => {
        if (!error.message) {
            console.log("async success ", data);
        } else {
            console.log("async ERROR ", error);
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
    console.log(istringholder.get());

    istringholder.setAsync("interface async set", (error: Error) => {
        if (!error.message) {
            console.log("interface async success ");
        } else {
            console.log("interface async ERROR ", error);
        }
    })

    let p_istringholder = istringholder.getPromise();
    p_istringholder
        .then((ret: NullishType) => {
            let retInner = ret as string;
            console.log("interface async success p_istringholder ", retInner)
        })
        .catch((ret: NullishType) => {
            let retError = ret as Error;
            console.error(
                "interface async promise ERROR p_istringholder ", retError)
        });
}