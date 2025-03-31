import * as bigint_test from "@generated/bigint_test";

loadLibrary("bigint");

function main() {
    console.info("bigint_test run start...");
    const suite = new ArkTestsuite("bigint_test ut")
    suite.addTest("testFromBigint", testFromBigint);
    suite.addTest("testToBigint", testToBigint);
    suite.run();
    console.info("bigint_test run end...");
}

function testFromBigint() {
    // test function GetNumfromBigint(b : BigInt) : long
    let big: BigInt = 666666666666666666666666666255n;
    let num: long = bigint_test.GetNumfromBigint(big);
    console.info("num : " + num);
    let result = (big % 256n).getLong();
    assertEQ(num, result);
}

function testToBigint() {
    // test function GenBigint(lg : long[]) : BigInt
    let array: long[] = [36140072416, 3384629513536841999];
    let result: BigInt = bigint_test.GenBigint(array);
    console.info("result : " + result);
    assertEQ(result, 666666666666666666666666666255n);
}
