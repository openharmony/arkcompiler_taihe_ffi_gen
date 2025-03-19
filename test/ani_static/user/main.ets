import * as lib from "../author_generated/staticTest"
loadLibrary("ani_static");

function main() {
    console.log("main ets")
    console.log("static method sum: ", lib.IBase.sumSync(10, 20))
    console.log("static method add: ", lib.IBase.addSync(10, 20))
    lib.IBase.add(10, 20, (error: Error, data?: int) => {
        if (!error.message) {
            console.log("main finsih test async success ", data);
        } else {
            console.log("main finsih test async ERROR ", error);
        }
    })

    try {
        let retPromise = await lib.IBase.add(0, 2);
        console.log("main finsih test async promise success ")
    } catch (error) {
        console.error("main finsih test async promise ERROR ", error)
    }

    let test = new lib.IBase("hello");
    console.log("new class: ", test.get());

    let test_1 = new lib.IBase("hello", "test");
    console.log("new class constructor 1: ", test_1.get());
}
