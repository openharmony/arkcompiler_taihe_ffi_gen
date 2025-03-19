import * as record_test from "../author_generated/record_test"
import { ICpu, Data } from "../author_generated/record_test"

loadLibrary("ani_record")

class A {
    constructor() {}
}

function main() {

    // test function getCpuSize(r: Record<string, ICpu>): int
    let cpu0 : ICpu = record_test.makeCpu();
    let cpu1 : ICpu = record_test.makeCpu();
    let cpus : Record<string, ICpu> = {
        'cpu0': cpu0,
        'cpu1': cpu1,
    }    
    let ret0 : int = record_test.getCpuSize(cpus);
    console.log(ret0);
    assertEQ(ret0, 2);

    // test function getASize(r: Record<int, NullishType>): int
    let a = new A();
    let b = new A();
    let c = new A();
    let As : Record<int, NullishType> = {
        0: a,
        1: b,
        2: c,
    }   
    let ret1 : int = record_test.getASize(As);
    console.log(ret1);
    assertEQ(ret1, 3);

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

    // test function createStringString(a: int): Record<string, string>
    let strRecord : Record<string, string> = record_test.createStringString(5);
    console.log(`Key: 0, Value: ` + strRecord["0"]);
    assertEQ(strRecord["0"], "abc");

    // test function getMapfromArray(d: (Data[])): Record<string, int>
    let d0 : Data = new Data('a', 1);
    let d1 : Data = new Data('b', 2);
    let d2 : Data = new Data('c', 3);
    let data : Data[] = [d0, d1, d2];
    let dataRecord : Record<string, int> = record_test.getMapfromArray(data);
    console.log(`Key: b, Value: ` + dataRecord["b"]);
    assertEQ(dataRecord["b"], 2);

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

