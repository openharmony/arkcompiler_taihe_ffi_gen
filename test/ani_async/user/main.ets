import * as async_test from "../author_generated/async_test"
loadLibrary("ani_async");

function main() {
    console.log("main ets")
    // In function addSync, we set it to throw an exception if the first parameter is equal to 0.
    console.log("in main ets: ", async_test.addSync(1, 2))

    async_test.add(10, 20, (error: Error, data?: int) => {
        if (!error.message) {
            console.log("main finsih test async success ", data);
        } else {
            console.log("main finsih test async ERROR ", error);
        }
    })

    try {
        let retPromise = await async_test.add(0, 2);
        console.log("main finsih test async promise success ")
    } catch (error) {
        console.error("main finsih test async promise ERROR ", error)
    }

    let ibase = async_test.getIBase();
    console.log(ibase.get());

    async_test.getIBaseAsync((error: Error, data?: async_test.IBase) => {
        if (!error.message) {
            console.log("main finsih test async success ", data!.get());
        } else {
            console.log("main finsih test async ERROR ", error);
        }
    })

    try {
        let retPromise = await async_test.getIBasePromise();
        console.log("main finsih test async promise success ")
    } catch (error) {
        console.error("main finsih test async promise ERROR ", error)
    }

    let data = new async_test.Data("abc", "efg", 3);
    async_test.fromStruct(data, (error: Error) => {
        if (!error.message) {
            console.log("main finsih test async success ");
        } else {
            console.log("main finsih test async ERROR ", error);
        }
    })

    try {
        let retPromise = await async_test.fromStruct(data);
        console.log("main finsih test async promise success ")
    } catch (error) {
        console.error("main finsih test async promise ERROR ", error)
    }

    async_test.toStruct("aaa", "bbb", 1, (error: Error, data?: async_test.Data) => {
        if (!error.message) {
            console.log("main finsih test async success ", data);
        } else {
            console.log("main finsih test async ERROR ", error);
        }
    })

    try {
        let retPromise = await async_test.toStruct("aaa", "bbb", 0);
        console.log("main finsih test async promise success ")
    } catch (error) {
        console.error("main finsih test async promise ERROR ", error)
    }

    let retPromise = async_test.toStruct("aaa", "bbb", 1);
    retPromise.then((ret: NullishType) => {
        let retInner = ret as async_test.Data;
        console.log("main finsih test async success retPromise ", retInner)
    })
    .catch((ret: NullishType) => {
        let retError = ret as Error;
        console.error("main finsih test async promise ERROR  retPromise ", retError)
    });

}
