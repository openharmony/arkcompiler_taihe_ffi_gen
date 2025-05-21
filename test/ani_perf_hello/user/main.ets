import * as hello from "hello";

loadLibrary("ani_perf_hello");

function runTestFunction(prompt: string, n: int, fn: () => void): void {
    const s = Chrono.nanoNow();
    for (let i: int = 0; i < n; i++) {
        fn();
    }
    const t = Chrono.nanoNow();
    let durationNs: double = (t - s) / n;
    console.log(`>> Done ${prompt}: ${durationNs / 1000} ms.`);
}

function testData() {
    hello.setData({
        a: "hello",
        b: 1.5,
        c: 12,
        d: true,
        f: false,
        g: true,
        e: false,
    });
    let data = hello.getData();
}

function testRecord() {
    hello.setRecord({
        "key1": "value1",
        "key2": "value2",
        "key3": "value3",
    });
    let rec = hello.getRecord();
}

function main() {
    runTestFunction("testData preheat", 500, testData);
    runTestFunction("testData test", 2000, testData);
    runTestFunction("testRecord preheat", 500, testRecord);
    runTestFunction("testRecord test", 2000, testRecord);
}
