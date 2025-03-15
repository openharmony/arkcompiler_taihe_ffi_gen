import * as test_primitives from "../author_generated/primitives_test"

function testMultiply(){
    let res = test_primitives.multiply(2, 4)
    assertEQ(res, 8)
}


function testFunC1(){
    let res = test_primitives.baseCFunc(10)
    assertEQ(res,true)
}

function testFunC2(){
    let res = test_primitives.baseCFunc(5)
    assertEQ(res,false)
}

function testFunA1(){
    test_primitives.baseAFunc(true)
}

function testFunA2(){
    test_primitives.baseAFunc(false)
}

function testFunB1(){
    let res = test_primitives.baseBFunc(true)
    assertEQ(res,false)
}

function testFunB2(){
    let res = test_primitives.baseBFunc(false)
    assertEQ(res,true)
}

function testFunD1(){
    let res = test_primitives.baseDFunc("test123")
    assertEQ(res,true)
}

function testFunD2(){
    let res = test_primitives.baseDFunc("test1231")
    assertEQ(res,false)
}

function testFunE(){
    const option: test_primitives.Foo = new test_primitives.Foo(
        2147483647,
        "path/to/source"
    )
    try {
        let res = test_primitives.baseEFunc(option)
        assertEQ(res,"success")
    } catch (error) {
        console.error("Failed to parse res:", error);
    }
}

function testFunH1(){
    let res = test_primitives.baseHFunc(2147483647,9223372036854775807)
    assertEQ(res,"-9223372034707292162")
}

function testFunH2(){
    let res = test_primitives.baseHFunc(-2147483648,-9223372036854775808)
    assertEQ(res,"9223372034707292160")
}

// function baseFunc1(){
//     let res = test_primitives.baseFunc1(3.0)
//     assertEQ(res,4.0)
// }

// function baseFunc2(){
//     test_primitives.baseFunc2(3.0)
// }


// function baseFunc3(){
//     let res =test_primitives.baseFunc3(3.0,3.14159265)
//     console.log("tests baseFunc3"+res)
// }

function baseFunc4(){
    let res =test_primitives.baseFunc4(3.0)
    console.log("tests baseFunc3"+res)
}

function baseFunc5(){
    test_primitives.baseFunc5(3.14159)
}

function baseFunc6(){
    test_primitives.baseFunc6("testbaseFunc6")
}

function baseFunc6_1(){
    test_primitives.baseFunc6("testbaseFunc66")
}

function baseFunc7(){
    let res = test_primitives.baseFunc7("testbaseFunc7")
    assertEQ(res,"testbaseFunc7")
}

function baseFunc7_1(){
    let res = test_primitives.baseFunc7("testbaseFunc77")
    assertEQ(res,"testbaseFunc77false")
}

function baseFunc8(){
    let res = test_primitives.baseFunc8("testbaseFunc8",32)
    assertEQ(res,"testbaseFunc832")
}

function baseFunc8_1(){
    let res = test_primitives.baseFunc8("testbaseFunc88",32)
    assertEQ(res,"testbaseFunc88")
}

//function baseFunc9(){
//    test_primitives.baseFunc9("testbaseFunc9",32,9223372036854775807,true,3.1)
//}


//Type 'double' is not compatible with type 'float' at index 2 [main.ets:71:58]
// function testFunI1(){
//     let res = test_primitives.baseIFunc(3.1415926535897931,4.3)
//     console.log("run main ... test_primitives ..."+res)
//     assertEQ(res,"-9223372034707292162")
// }

// function testFunI2(){
//     let res = test_primitives.baseIFunc(-1234567890.1234567,-123.4)
//     console.log("run main ... test_primitives ..."+res)
//     assertEQ(res,"9223372034707292160")
// }


function baseFunc10(){
    test_primitives.baseFunc10()
}

function baseFunc11(){
    test_primitives.baseFunc11(32,true)
}

function baseFunc11_1(){
    test_primitives.baseFunc11(32,false)
}

function baseFunc12(){
    test_primitives.baseFunc12(32,92233720368547758)
}

function baseFunc13(){
    test_primitives.baseFunc13(32,"testbaseFunc13")
}

function baseFunc14(){
    test_primitives.baseFunc14(92233720368547758,true)
}


function baseFunc14_1(){
    test_primitives.baseFunc14(92233720368547758,false)
}

//function baseFunc15(){
//   test_primitives.baseFunc15(32,3.15)
//}

function baseFunc16(){
    test_primitives.baseFunc16(32,3.141592653589793)
}

function baseFunc16_1(){
    test_primitives.baseFunc16(32,3.-3.141592653589793)
}


//function baseFunc17(){
//    test_primitives.baseFunc17(123.456,true)
//}

//function baseFunc17_1(){
//    test_primitives.baseFunc17(3.14159,false)
//}

//function baseFunc18(){
//    test_primitives.baseFunc18(123.456,"testbaseFunc18")
//}

//function baseFunc18_1(){
//   test_primitives.baseFunc18(3.14159,"testbaseFunc18")
//}

function baseFunc19(){
    test_primitives.baseFunc19(3.141592653589793,"testbaseFunc19")
}

function baseFunc20(){
    test_primitives.baseFunc20(3.141592653589793,true)
}

function baseFunc20_1(){
    test_primitives.baseFunc20(3.141592653589793,false)
}

function main() {
    console.log("run main ... test_primitives ...")
    
    const suite = new ArkTestsuite ("test function primitives")

	suite.addTest("check funcMultiply", testMultiply)
    suite.addTest("check testFunC1", testFunC1)
    suite.addTest("check testFunC2", testFunC2)
    suite.addTest("check testFunA1", testFunA1)
    suite.addTest("check testFunA2", testFunA2)
    suite.addTest("check testFunB1", testFunB1)
    suite.addTest("check testFunB2", testFunB2)
    suite.addTest("check testFunD1", testFunD1)
    suite.addTest("check testFunD2", testFunD2)
    suite.addTest("check testFunE", testFunE)
    suite.addTest("check testFunH1", testFunH1)
    suite.addTest("check testFunH2", testFunH2)
    // suite.addTest("check testFunI1", testFunI1)
    // suite.addTest("check testFunI2", testFunI2)
    // suite.addTest("check testbaseFunc1", baseFunc1)
    // suite.addTest("check testbaseFunc2", baseFunc2)
    // suite.addTest("check testbaseFunc3", baseFunc3)
    suite.addTest("check testbaseFunc4", baseFunc4)
    suite.addTest("check testbaseFunc5", baseFunc5)
    suite.addTest("check testbaseFunc6", baseFunc6)
    suite.addTest("check testbaseFunc7", baseFunc7)
    suite.addTest("check testbaseFunc8", baseFunc8)
    suite.addTest("check testbaseFunc6_1", baseFunc6_1)
    suite.addTest("check testbaseFunc7_1", baseFunc7_1)
    suite.addTest("check testbaseFunc8_1", baseFunc8_1)
    // suite.addTest("check testbaseFunc9", baseFunc9)
    suite.addTest("check testbaseFunc10", baseFunc10)
    suite.addTest("check testbaseFunc11", baseFunc11)
    suite.addTest("check testbaseFunc11_1", baseFunc11_1)
    suite.addTest("check testbaseFunc12", baseFunc12)
    suite.addTest("check testbaseFunc13", baseFunc13)
    suite.addTest("check testbaseFunc14", baseFunc14)
    suite.addTest("check testbaseFunc14_1", baseFunc14_1)
    //suite.addTest("check testbaseFunc15", baseFunc15)
    suite.addTest("check testbaseFunc16", baseFunc16)
    suite.addTest("check testbaseFunc16_1", baseFunc16_1)
    //suite.addTest("check testbaseFunc17", baseFunc17)
    //suite.addTest("check testbaseFunc17_1", baseFunc17_1)
    //suite.addTest("check testbaseFunc18", baseFunc18)
    //suite.addTest("check testbaseFunc18_1", baseFunc18_1)
    suite.addTest("check testbaseFunc19", baseFunc19)
    suite.addTest("check testbaseFunc20", baseFunc20)
    suite.addTest("check testbaseFunc20_1", baseFunc20_1)
    suite.run()
    // console.log(test_primitives.baseFFunc(1,12345.678))
    // console.log(test_primitives.baseFFunc(1,3.4e38))
}