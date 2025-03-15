import * as ani_callback from "../author_generated/ani_callback"
loadLibrary("ani_callback");

function main() {
    console.log("main ets")
    // In function addSync, we set it to throw an exception if the first parameter is equal to 0.
    console.log("in main ets: ", ani_callback.addSync(1, 2))

    ani_callback.add(10, 20, (error: Error, data?: int) => {
        if (!error.message) {
            console.log("main finsih test callback success ", data);
        } else {
            console.log("main finsih test callback ERROR ", error);
        }
    })

    try {
        let retPromise = await ani_callback.add(0, 2);
        console.log("main finsih test callback promise success ")
    } catch (error) {
        console.error("main finsih test callback promise ERROR ", error)
    }

    let ibase = ani_callback.getIBase();
    console.log(ibase.get());

    ani_callback.getIBaseAsync((error: Error, data?: ani_callback.IBase) => {
        if (!error.message) {
            console.log("main finsih test callback success ", data!.get());
        } else {
            console.log("main finsih test callback ERROR ", error);
        }
    })

    try {
        let retPromise = await ani_callback.getIBasePromise();
        console.log("main finsih test callback promise success ")
    } catch (error) {
        console.error("main finsih test callback promise ERROR ", error)
    }

    let data = new ani_callback.Data("abc", "efg", 3);
    ani_callback.fromStruct(data, (error: Error) => {
        if (!error.message) {
            console.log("main finsih test callback success ");
        } else {
            console.log("main finsih test callback ERROR ", error);
        }
    })

    try {
        let retPromise = await ani_callback.fromStruct(data);
        console.log("main finsih test callback promise success ")
    } catch (error) {
        console.error("main finsih test callback promise ERROR ", error)
    }

    ani_callback.toStruct("aaa", "bbb", 1, (error: Error, data?: ani_callback.Data) => {
        if (!error.message) {
            console.log("main finsih test callback success ", data);
        } else {
            console.log("main finsih test callback ERROR ", error);
        }
    })

    try {
        let retPromise = await ani_callback.toStruct("aaa", "bbb", 0);
        console.log("main finsih test callback promise success ")
    } catch (error) {
        console.error("main finsih test callback promise ERROR ", error)
    }

    let retPromise = ani_callback.toStruct("aaa", "bbb", 1);
    retPromise.then((ret: NullishType) => {
        let retInner = ret as ani_callback.Data;
        console.log("main finsih test callback success retPromise ", retInner)
    })
    .catch((ret: NullishType) => {
        let retError = ret as Error;
        console.error("main finsih test callback promise ERROR  retPromise ", retError)
    });

}
