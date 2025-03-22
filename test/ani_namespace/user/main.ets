import * as namespaceTest from "../author_generated/ns_alltest"

loadLibrary("ani_namespace")


function testCasebaseFunctionTest1(){
    namespaceTest.functiontest.baseFunctionTest1()
}

function testCasebaseFunctionTest2(){
    namespaceTest.functiontest.baseFunctionTest2(127 as byte)
}

function testCasebaseFunctionTest3(){
    namespaceTest.functiontest.baseFunctionTest3(255 as short)
}

function testCasebaseFunctionTest4(){
    namespaceTest.functiontest.baseFunctionTest4(2147483647)
}

function testCasebaseFunctionTest5(){
    namespaceTest.functiontest.baseFunctionTest5(9223372036854775807)
}

function testCasebaseFunctionTest6(){
    namespaceTest.functiontest.baseFunctionTest6(3.1415 as float)
}

function testCasebaseFunctionTest7(){
    namespaceTest.functiontest.baseFunctionTest7(3.1415125)
}

function testCasebaseFunctionTest8(){
    namespaceTest.functiontest.baseFunctionTest8("baseFunctionTest8!@#$%%^&*()")
}

function testCasebaseFunctionTest9(){
    namespaceTest.functiontest.baseFunctionTest9(false)
}

function testCasebaseFunctionTest10(){
    let byteArray:byte[] = [1,127,-120,0,100];
    namespaceTest.functiontest.baseFunctionTest10(byteArray)
}

function testCasebaseFunctionTest11(){
    let shortArray:short[] = [32767,-32768,122,50,10086];
    namespaceTest.functiontest.baseFunctionTest11(shortArray)
}

function testCasebaseFunctionTest12(){
    namespaceTest.functiontest.baseFunctionTest12(255 as short)
}

function testCasebaseFunctionTest12_1(){
    namespaceTest.functiontest.baseFunctionTest12(undefined)
}

function testCasebaseFunctionTest13(){
    namespaceTest.functiontest.baseFunctionTest13(9223372036854775807)
}

function testCasebaseFunctionTest13_1(){
    namespaceTest.functiontest.baseFunctionTest13(undefined)
}

function testCasebaseFunctionTest14(){
    let numbersU8: byte[] = [1, 2, 3, 4, 5];
    let arrbuf1: ArrayBuffer = new ArrayBuffer(numbersU8.length);
    for (let i = 0; i < numbersU8.length; i++) {
        arrbuf1.set(i, numbersU8[i]);
    }
    namespaceTest.functiontest.baseFunctionTest14(arrbuf1)
}

function testCasebaseFunctionTest15(){
    let record : Record<string, int> = {
        "test1": 0,
        "test2": 1,
        "test3": 2,
        "test4": 3,
    };
    namespaceTest.functiontest.baseFunctionTest15(record)
}

function testCasebaseFunctionTest16(){
    let res = namespaceTest.functiontest.baseFunctionTest16(110 as byte);
    assertEQ(res,120)
}

function testCasebaseFunctionTest16_1(){
    try {
         let res = namespaceTest.functiontest.baseFunctionTest16(127 as byte);
    } catch (e) {
        assertEQ(e.toString(),  "Error: baseFunctionTest16: result exceeds int8_t range")    
    }
}

function testCasebaseFunctionTest17(){
    let res = namespaceTest.functiontest.baseFunctionTest17(3270 as short);
    assertEQ(res,32700)
}

function testCasebaseFunctionTest17_1(){
    try {
         let res = namespaceTest.functiontest.baseFunctionTest17(32767 as short);
    } catch (e) {
        assertEQ(e.toString(),  "Error: baseFunctionTest17: result exceeds int16_t range")    
    }
}

function testCasebaseFunctionTest18(){
    let res = namespaceTest.functiontest.baseFunctionTest18(21474836);
    assertEQ(res,2147483600)
}

function testCasebaseFunctionTest18_1(){
    try {
         let res = namespaceTest.functiontest.baseFunctionTest18(21474837);
    } catch (e) {
        console.log("testCasebaseFunctionTest18_1 error ",e.toString())
        assertEQ(e.toString(),  "Error: baseFunctionTest18: result exceeds int32_t range")    
    }
}

function testCasebaseFunctionTest19(){
    let res = namespaceTest.functiontest.baseFunctionTest19(92233720368547758);
    assertEQ(res,922337203685477580)
}

function testCasebaseFunctionTest20(){
    let res = namespaceTest.functiontest.baseFunctionTest20(3.14 as float);
    assertEQ(res,103.14 as float)
}

function testCasebaseFunctionTest21(){
    let res = namespaceTest.functiontest.baseFunctionTest21(1);
    assertEQ(res,2.01)
}

function testCasebaseFunctionTest22(){
    let res = namespaceTest.functiontest.baseFunctionTest22("baseFunctionTest22");
    assertEQ(res,"baseFunctionTest22hello ani")
}

function testCasebaseFunctionTest22_1(){
    let res = namespaceTest.functiontest.baseFunctionTest22("baseFunctionTest22——1");
    assertEQ(res,"baseFunctionTest22——1")
}

function testCasebaseFunctionTest23(){
    let res = namespaceTest.functiontest.baseFunctionTest23(true);
    assertEQ(res,false)
}

function testCasebaseFunctionTest23_1(){
    let res = namespaceTest.functiontest.baseFunctionTest23(false);
    assertEQ(res,true)
}

function testCasebaseFunctionTest24(){
    let byteArray: byte[] = [1, 2, 3, 4, 5];
    let res = namespaceTest.functiontest.baseFunctionTest24(byteArray);
    let temp:byte[] = [2,4,6,8,10];
    for (let i = 0; i < res.length; i++) {
        assertEQ(res[i], temp[i])
    }
}

function testCasebaseFunctionTest25(){
    let shortArray: short[] = [1, 2, 3, 4, 5];
    let res = namespaceTest.functiontest.baseFunctionTest25(shortArray);
    let temp:byte[] = [3,4,5,6,7];
    for (let i = 0; i < res.length; i++) {
        assertEQ(res[i], temp[i])
    }
}

function testCasebaseFunctionTest26(){
    let res = namespaceTest.functiontest.baseFunctionTest26(3276 as short);
    assertEQ(res,3286)
}

function testCasebaseFunctionTest26_1(){
    let res = namespaceTest.functiontest.baseFunctionTest26(undefined);
    assertEQ(res,undefined)
}

function testCasebaseFunctionTest27(){
    let res = namespaceTest.functiontest.baseFunctionTest27(922337203685477580);
    assertEQ(res,922337203685477590)
}

function testCasebaseFunctionTest27_1(){
    let res = namespaceTest.functiontest.baseFunctionTest27(undefined);
    assertEQ(res,undefined)
}

function testCasebaseFunctionTest28(){
    let numbersU8: byte[] = [11, 2, 3, 4, 5];
    let arrbuf1: ArrayBuffer = new ArrayBuffer(numbersU8.length);
    for (let i = 0; i < numbersU8.length; i++) {
        arrbuf1.set(i, numbersU8[i]);
    }
    let res = namespaceTest.functiontest.baseFunctionTest28(arrbuf1);
    console.log("testCasebaseFunctionTest28 length: " + res.getByteLength());
    console.log("testCasebaseFunctionTest28 : " + res);
    assertEQ(res.getByteLength(), 5)    
    for (let i = 0; i < res.getByteLength(); i++) {
        console.log(`testCasebaseFunctionTest28 Byte at index ${i}: ${res.at(i)}`);
        assertEQ(res.at(i), numbersU8[i] * 10)
    }
}

function testCasebaseFunctionTest29(){
    const myRecord: Record<string, int> = {
    "key1": 10,
    "key2": 20,
    "key3": 30, 
    };

    const resultRecord: Record<string, int> = {
    "test0": 10,
    "test1": 11,
    "test2": 12, 
    };
    let res = namespaceTest.functiontest.baseFunctionTest29(myRecord);
    console.log("testCasebaseFunctionTest29 ",res);
    console.log("testCasebaseFunctionTest29 test0 ",res["test0"]);
    assertEQ(res["test0"],resultRecord["test0"]);
    assertEQ(res["test1"],resultRecord["test1"]);
    assertEQ(res["test2"],resultRecord["test2"]);
}

function testCasebaseFunctionTest30(){
    let color= namespaceTest.functiontest.Color.BLUE;
    let res = namespaceTest.functiontest.baseFunctionTest30(color);
    console.log("testCasebaseFunctionTest30 ",res)
    assertEQ(res,namespaceTest.functiontest.Color.RED)
}

function testCasebaseFunctionTest31(){
    let color = namespaceTest.functiontest.Color.RED;
    namespaceTest.functiontest.baseFunctionTest31(color);
}

function testCasebaseFunctionTest32(){
    let int16Array:short[] = [121,100,32767,-32768,0];
    let int64Array:long[] = [9223372036854775807,-100,121,-2147483648,-9223372036854775808];
    let res = namespaceTest.functiontest.baseFunctionTest32(127 as byte,100 as short,256,10000,3.14 as float,-2.0002,"test1",true,int16Array,int64Array);
    assertEQ(res,100)
}

function testCasebaseFunctionTest32_1(){
    let int16Array:short[] = [121,100,32767,-32768,0];
    let int64Array:long[] = [9223372036854775807,-100,121,-2147483648,-9223372036854775808];
    let res = namespaceTest.functiontest.baseFunctionTest32(127 as byte,100 as short,256,10000,3.14 as float,-2.0002,"test1",false,int16Array,int64Array);
    assertEQ(res,127)
}

function testCasebaseFunctionTest33(){
    let byteArray:byte[] = [1,2,3,4,5];
    let intArray:int[] = [922337,-100,121,-2147483648,-92233720];
    let res = namespaceTest.functiontest.baseFunctionTest33(127 as byte,100 as short,256,10000,3.14 as float,-2.0002,"test1",true,byteArray,intArray);
    assertEQ(res,256)
}

function testCasebaseFunctionTest33_1(){
    let byteArray:byte[] = [1,2,3,4,5];
    let intArray:int[] = [922337,-100,121,-2147483648,-92233720];
    let res = namespaceTest.functiontest.baseFunctionTest33(127 as byte,100 as short,256,10000,3.14 as float,-2.0002,"test1",false,byteArray,intArray);
    assertEQ(res,100)
}

function testCasebaseFunctionTest34(){
    let strArray:string[] = ["test1","test2","test3","test4","test5"];
    let int64Array:long[] = [9223372036854775807,-100,121,-2147483648,-9223372036854775808];
    let res = namespaceTest.functiontest.baseFunctionTest34(127 as byte,100 as short,256,10000,3.14 as float,-2.0002,"test1",true,strArray,int64Array);
    assertEQ(res,10000)
}

function testCasebaseFunctionTest34_1(){
    let strArray:string[] = ["test1","test2","test3","test4","test5"];
    let int64Array:long[] = [9223372036854775807,-100,121,-2147483648,-9223372036854775808];
    let res = namespaceTest.functiontest.baseFunctionTest34(127 as byte,100 as short,256,10000,3.14 as float,-2.0002,"test1",false,strArray,int64Array);
    assertEQ(res,100)
}

function testCasebaseFunctionTest35(){
    let boolArray:boolean[] = [true,false,true,false,true];
    let int64Array:long[] = [9223372036854775807,-100,121,-2147483648,-9223372036854775808];
    let res = namespaceTest.functiontest.baseFunctionTest35(127 as byte,100 as short,256,10000,3.14 as float,-2.0002,"test1",true,boolArray,int64Array);
    assertEQ(res,127)
}

function testCasebaseFunctionTest35_1(){
    let boolArray:boolean[] = [true,false,true,false,true];
    let int64Array:long[] = [9223372036854775807,-100,121,-2147483648,-9223372036854775808];
    let res = namespaceTest.functiontest.baseFunctionTest35(127 as byte,100 as short,256,10000,3.14 as float,-2.0002,"test1",false,boolArray,int64Array);
    assertEQ(res,100)
}

function testCasebaseFunctionTest36(){
    let int8Array:byte[] = [1,2,3,4,5];
    let int64Array:long[] = [9223372036854775807,-100,121,-2147483648,-9223372036854775808];
    let res = namespaceTest.functiontest.baseFunctionTest36(10 as byte,11 as short,12,10000,3.14 as float,-2.0002,"test1",true,int8Array,int64Array);
    assertEQ(res.length,int8Array.length)
    let tempResult:int[] = [34,35,36,37,38]
    for (let i:int = 0; i < res.length; i++) {
        assertEQ(res[i], tempResult[i])
    }
}

function testCasebaseFunctionTest36_1(){
    let int8Array:byte[] = [1,2,3,4,5];
    let int64Array:long[] = [100,-100,200,-300,-400];
    let res = namespaceTest.functiontest.baseFunctionTest36(127 as byte,100 as short,256,10000,3.14 as float,-2.0002,"test1",false,int8Array,int64Array);
    assertEQ(res.length,int64Array.length)
    for (let i:int = 0; i < res.length; i++) {
        assertEQ(res[i], int64Array[i])
    }
}

function testCasebaseFunctionTest37(){
    let intArray:int[] = [922337,-100,121,-2147483648,-92233720];
    let int64Array:long[] = [100,-100,121,-200,0];
    let res = namespaceTest.functiontest.baseFunctionTest37(10 as byte,11 as short,12,10000,3.14 as float,-2.0002,"test1",true,intArray,int64Array);
    assertEQ(res.length,int64Array.length)
    let tempResult:int[] = [133,-67,154,-167,33]
    for (let i:int = 0; i < res.length; i++) {
        assertEQ(res[i], tempResult[i])
    }
}

function testCasebaseFunctionTest37_1(){
    let intArray:int[] = [922337,-100,121,-2147483648,-92233720];
    let int64Array:long[] = [100,-100,200,-300,-400];
    let res = namespaceTest.functiontest.baseFunctionTest37(127 as byte,100 as short,256,10000,3.14 as float,-2.0002,"test1",false,intArray,int64Array);
    assertEQ(res.length,int64Array.length)
    for (let i:int = 0; i < res.length; i++) {
        assertEQ(res[i], int64Array[i]*10)
    }
}

function testCasebaseFunctionTest38(){
    let byteArray:byte[] = [1,2,3,4,5];
    let int16Array:short[] = [100,-100,121,-200,-500];
    let res = namespaceTest.functiontest.baseFunctionTest38(10 as byte,11 as short,12,10000,3.14 as float,-2.0002,"test1",true,byteArray,int16Array);
    assertEQ(res,"test110111210000")
}

function testCasebaseFunctionTest38_1(){
    let byteArray:byte[] = [1,2,3,4,5];
    let int16Array:short[] = [100,-100,121,-200,-500];
    let res = namespaceTest.functiontest.baseFunctionTest38(127 as byte,100 as short,256,10000,3.14 as float,-2.0002,"test1",false,byteArray,int16Array);
    assertEQ(res,"test11100")
}

function testCasebaseFunctionTest39(){
    let boolArray:boolean[] = [true,false,true,false,true];
    let intArray:int[] = [922337,-100,121,-2147483648,-92233720];
    let res = namespaceTest.functiontest.baseFunctionTest39(10 as byte,11 as short,12,10000,3.14 as float,-2.0002,"test1",true,boolArray,intArray);
    assertEQ(res,false)
}

function testCasebaseFunctionTest39_1(){
    let boolArray:boolean[] = [true,false,true,false,true];
    let intArray:int[] = [922337,-100,121,-2147483648,-92233720];
    let res = namespaceTest.functiontest.baseFunctionTest39(127 as byte,100 as short,256,10000,3.14 as float,-2.0002,"test1",false,boolArray,intArray);
    assertEQ(res,false)
}

function testCasebaseFunctionTest40(){
    let byteArray:byte[] = [1, 2, 3, 4, 5];
    let numbersU8: byte[] = [10, 20, 30, 40, 50];
    let arrbuf1: ArrayBuffer = new ArrayBuffer(numbersU8.length);
    for (let i = 0; i < numbersU8.length; i++) {
        arrbuf1.set(i, numbersU8[i])
    }
    let res = namespaceTest.functiontest.baseFunctionTest40(10 as byte,11 as short,12,10000,3.14 as float,-2.0002,"test1",true,byteArray,arrbuf1);
    assertEQ(res.length,byteArray.length)
    for (let i:int = 0; i < res.length; i++) {
        assertEQ(res[i], byteArray[i]*2)
    }
}

function testCasebaseFunctionTest40_1(){
    let byteArray:byte[] = [1, 2, 3, 4, 5];
    let numbersU8: byte[] = [10, 20, 30, 40, 50];
    let arrbuf1: ArrayBuffer = new ArrayBuffer(numbersU8.length);
    for (let i = 0; i < numbersU8.length; i++) {
        arrbuf1.set(i, numbersU8[i])
    }
    let res = namespaceTest.functiontest.baseFunctionTest40(127 as byte,100 as short,256,10000,3.14 as float,-2.0002,"test1",false,byteArray,arrbuf1);
     assertEQ(res.length,byteArray.length)
    for (let i:int = 0; i < res.length; i++) {
        assertEQ(res[i], byteArray[i]+10)
    }
}

function testCasebaseFunctionTest41(){
    let int16Array:short[] = [121,100,32767,-32768,0];
    let int64Array:long[] = [100,-100,9223372036854775807,-300,-9223372036854775808];
    namespaceTest.functiontest.baseFunctionTest41(10 as byte,11 as short,12,10000,3.14 as float,-2.0002,"test41",true,int16Array,int64Array);
}
function testCasebaseFunctionTest42(){
    let res = namespaceTest.functiontest.baseFunctionTest42(10000,256 as short);
    assertEQ(res,10256)
}

function testCasebaseFunctionTest42_1(){
    try{
        let res = namespaceTest.functiontest.baseFunctionTest42(2147483647,256 as short);
    } catch (e) {
        console.log("testCasebaseFunctionTest42_1 e ",e.toString())
        assertEQ(e.toString(),  "Error: baseFunctionTest42_int: result exceeds int32_t range")    
    }
}

function testCasebaseFunctionTest43(){
    let record : Record<string, int> = {
        "test1": 0,
        "test2": 1,
        "test3": 2,
    };
    let res = namespaceTest.functiontest.baseFunctionTest42(10000,record);
    assertEQ(res,10010)
}

function testCasebaseFunctionTest43_1(){
    let record : Record<string, int> = {
        "test1": 0,
        "test2": 1,
        "test3": 2,
    };
    let res = namespaceTest.functiontest.baseFunctionTest42(undefined,record);
    assertEQ(res,-2147483648)
}

function testCasebaseFunctionTest44(){
    let res = namespaceTest.functiontest.baseFunctionTest42();
    assertEQ(res,2147483647)
}

function testCasebaseFunctionTest45(){
    const testData: namespaceTest.functiontest.Data = new namespaceTest.functiontest.Data(
        "baseFunctionTest42",
        true,
        2147483647
    )
    namespaceTest.functiontest.baseFunctionTest42(testData);
}

function main() {
    console.log("run main ... ani_namespace_test begin ...")
    const suite = new ArkTestsuite ("test function namespace_test")

	suite.addTest("check testCasebaseFunctionTest1", testCasebaseFunctionTest1)
    suite.addTest("check testCasebaseFunctionTest2", testCasebaseFunctionTest2)
    suite.addTest("check testCasebaseFunctionTest3", testCasebaseFunctionTest3)
    suite.addTest("check testCasebaseFunctionTest4", testCasebaseFunctionTest4)
    suite.addTest("check testCasebaseFunctionTest5", testCasebaseFunctionTest5)
    suite.addTest("check testCasebaseFunctionTest6", testCasebaseFunctionTest6)
    suite.addTest("check testCasebaseFunctionTest7", testCasebaseFunctionTest7)
    suite.addTest("check testCasebaseFunctionTest8", testCasebaseFunctionTest8)
    suite.addTest("check testCasebaseFunctionTest9", testCasebaseFunctionTest9)
    suite.addTest("check testCasebaseFunctionTest10", testCasebaseFunctionTest10)
    suite.addTest("check testCasebaseFunctionTest11", testCasebaseFunctionTest11)
    suite.addTest("check testCasebaseFunctionTest12", testCasebaseFunctionTest12)
    suite.addTest("check testCasebaseFunctionTest12_1", testCasebaseFunctionTest12_1)
    suite.addTest("check testCasebaseFunctionTest13", testCasebaseFunctionTest13)
    suite.addTest("check testCasebaseFunctionTest13_1", testCasebaseFunctionTest13_1)
    suite.addTest("check testCasebaseFunctionTest14", testCasebaseFunctionTest14)
    suite.addTest("check testCasebaseFunctionTest15", testCasebaseFunctionTest15)
    suite.addTest("check testCasebaseFunctionTest16", testCasebaseFunctionTest16)
    suite.addTest("check testCasebaseFunctionTest16_1", testCasebaseFunctionTest16_1)
    suite.addTest("check testCasebaseFunctionTest17", testCasebaseFunctionTest17)
    suite.addTest("check testCasebaseFunctionTest17_1", testCasebaseFunctionTest17_1)
    suite.addTest("check testCasebaseFunctionTest18", testCasebaseFunctionTest18)
    suite.addTest("check testCasebaseFunctionTest18_1", testCasebaseFunctionTest18_1)
    suite.addTest("check testCasebaseFunctionTest19", testCasebaseFunctionTest19)
    suite.addTest("check testCasebaseFunctionTest20", testCasebaseFunctionTest20)
    suite.addTest("check testCasebaseFunctionTest21", testCasebaseFunctionTest21)
    suite.addTest("check testCasebaseFunctionTest22", testCasebaseFunctionTest22)
    suite.addTest("check testCasebaseFunctionTest22_1", testCasebaseFunctionTest22_1)
    suite.addTest("check testCasebaseFunctionTest23", testCasebaseFunctionTest23)
    suite.addTest("check testCasebaseFunctionTest23_1", testCasebaseFunctionTest23_1)
    suite.addTest("check testCasebaseFunctionTest24", testCasebaseFunctionTest24)
    suite.addTest("check testCasebaseFunctionTest25", testCasebaseFunctionTest25)
    suite.addTest("check testCasebaseFunctionTest26", testCasebaseFunctionTest26)
    suite.addTest("check testCasebaseFunctionTest26_1", testCasebaseFunctionTest26_1)
    suite.addTest("check testCasebaseFunctionTest27", testCasebaseFunctionTest27)
    suite.addTest("check testCasebaseFunctionTest27_1", testCasebaseFunctionTest27_1)
    suite.addTest("check testCasebaseFunctionTest28", testCasebaseFunctionTest28)
    suite.addTest("check testCasebaseFunctionTest29", testCasebaseFunctionTest29)
    suite.addTest("check testCasebaseFunctionTest30", testCasebaseFunctionTest30)
    suite.addTest("check testCasebaseFunctionTest31", testCasebaseFunctionTest31)
    suite.addTest("check testCasebaseFunctionTest32", testCasebaseFunctionTest32)
    suite.addTest("check testCasebaseFunctionTest32_1", testCasebaseFunctionTest32_1)
    suite.addTest("check testCasebaseFunctionTest33", testCasebaseFunctionTest33)
    suite.addTest("check testCasebaseFunctionTest33_1", testCasebaseFunctionTest33_1)
    suite.addTest("check testCasebaseFunctionTest34", testCasebaseFunctionTest34)
    suite.addTest("check testCasebaseFunctionTest34_1", testCasebaseFunctionTest34_1)
    suite.addTest("check testCasebaseFunctionTest35", testCasebaseFunctionTest35)
    suite.addTest("check testCasebaseFunctionTest35_1", testCasebaseFunctionTest35_1)
    suite.addTest("check testCasebaseFunctionTest36", testCasebaseFunctionTest36)
    suite.addTest("check testCasebaseFunctionTest36_1", testCasebaseFunctionTest36_1)
    suite.addTest("check testCasebaseFunctionTest37", testCasebaseFunctionTest37)
    suite.addTest("check testCasebaseFunctionTest37_1", testCasebaseFunctionTest37_1)
    suite.addTest("check testCasebaseFunctionTest38", testCasebaseFunctionTest38)
    suite.addTest("check testCasebaseFunctionTest38_1", testCasebaseFunctionTest38_1)
    suite.addTest("check testCasebaseFunctionTest39", testCasebaseFunctionTest39)
    suite.addTest("check testCasebaseFunctionTest39_1", testCasebaseFunctionTest39_1)
    suite.addTest("check testCasebaseFunctionTest40", testCasebaseFunctionTest40)
    suite.addTest("check testCasebaseFunctionTest40_1", testCasebaseFunctionTest40_1)
    suite.addTest("check testCasebaseFunctionTest41", testCasebaseFunctionTest41)
    suite.addTest("check testCasebaseFunctionTest42", testCasebaseFunctionTest42)
    suite.addTest("check testCasebaseFunctionTest42_1", testCasebaseFunctionTest42_1)
    suite.addTest("check testCasebaseFunctionTest43", testCasebaseFunctionTest43)
    suite.addTest("check testCasebaseFunctionTest43_1", testCasebaseFunctionTest43_1)
    suite.run()
    
}
