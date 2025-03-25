import * as record_test from "../author_generated/record_test"
import { ICpu, Data } from "../author_generated/record_test"

loadLibrary("ani_record")

class A {
    constructor() {}
}

function getCpuSize() {
    // test function getCpuSize(r: Record<string, ICpu>): int
    let cpu0 : ICpu = record_test.makeCpu();
    let cpu1 : ICpu = record_test.makeCpu();
    let cpus : Record<string, ICpu> = {
        'cpu0': cpu0,
        'cpu1': cpu1,
    };
    let ret0 : int = record_test.getCpuSize(cpus);
    console.log(ret0);
    assertEQ(ret0, 2);
}

function getASize() {
    // test function getASize(r: Record<int, NullishType>): int
    let a = new A();
    let b = new A();
    let c = new A();
    let As : Record<int, NullishType> = {
        0: a,
        1: b,
        2: c,
    };
    let ret1 : int = record_test.getASize(As);
    console.log(ret1);
    assertEQ(ret1, 3);
}

function getStringIntSize() {
    // test function getStringIntSize(r: Record<string, int>): int
    let record : Record<string, int> = {
        'aaa': 0,
        'bbb': 1,
        'ccc': 2,
        'ddd': 3,
    };
    let ret2 : int = record_test.getStringIntSize(record);
    console.log(ret2);
    assertEQ(ret2, 4);
}

function createStringString() {
    // test function createStringString(a: int): Record<string, string>
    let strRecord : Record<string, string> = record_test.createStringString(5);
    console.log(`Key: 0, Value: ` + strRecord["0"]);
    assertEQ(strRecord["0"], "abc");
}

function getMapfromArray() {
    // test function getMapfromArray(d: (Data[])): Record<string, int>
    let d0 : Data = new Data('a', 1);
    let d1 : Data = new Data('b', 2);
    let d2 : Data = new Data('c', 3);
    let data : Data[] = [d0, d1, d2];
    let dataRecord : Record<string, int> = record_test.getMapfromArray(data);
    console.log(`Key: b, Value: ` + dataRecord["b"]);
    assertEQ(dataRecord["b"], 2);
}

function getDatafromMap() {
    // test function getDatafromMap(m: Record<string, Data>, k: string): Data
    let data1 : Data = new Data('aaa', 1);
    let data2 : Data = new Data('bbb', 2);
    let data3 : Data = new Data('ccc', 3);
    let drecord : Record<string, Data> = {
        'aa': data1,
        'bb': data2,
        'cc': data3,
    };
    let d : Data = record_test.getDatafromMap(drecord, 'bb');
    console.log(`Data Value: ` + d.a);
    assertEQ(d.a, "bbb");
}

function main() {

    console.log("##############start#############")
    const suite = new ArkTestsuite ("record ut")

    suite.addTest("get Cpu Size test", getCpuSize)
    suite.addTest("get A Size test", getASize)
    suite.addTest("get String Int Size test", getStringIntSize)
    suite.addTest("create String String test", createStringString)
    suite.addTest("get Map from Array test", getMapfromArray)
    suite.addTest("get Data from Map test", getDatafromMap)
    suite.run()
}

