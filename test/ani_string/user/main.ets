import * as StringIo from "../author_generated/string_io"
import * as StringOp from "../author_generated/string_op"

loadLibrary("ani_string")

function concatString() {
    let str = StringOp.concatString("abc", "d");
    assertEQ(str, "abcd")
}

function makeString() {
    let str = StringOp.makeString("abc", 3);
    assertEQ(str, "abcabcabc")
}

function split() {
    let strPair = StringOp.split("abcd", 2);
    assertEQ(strPair._0, "ab")
    assertEQ(strPair._1, "cd")
}

function to_i32() {
    let num = StringOp.to_i32("123");
    assertEQ(num, 123)
}

function from_i32() {
    let str = StringOp.from_i32(123);
    assertEQ(str, "123")
}

function input() {
    let str = StringIo.input();
    assertEQ(str, "input")
}

function println() {
    StringIo.println("println string");
}

function print() {
    StringIo.print("print string");
    StringIo.println(" ---");
}

function testPlayString() {
    let playStr = StringOp.makePlayStringIface();
    assertEQ(playStr.name, "PlayString")

    let res = playStr.pickString(["abc", "edf", "xyz"], 1, 2)
    assertEQ(res, "edfxyz")

    res = playStr.pickString(["abc", "edf", "xyz"], 0, 1)
    assertEQ(res, "abcedf")
}

function main() {
    console.log("run main ... StringTest ...")

    const suite = new ArkTestsuite("StringTest")
    suite.addTest("concatString", concatString)
    suite.addTest("makeString", makeString)
    suite.addTest("split", split)
    suite.addTest("to_i32", to_i32)
    suite.addTest("from_i32", from_i32)
    suite.addTest("input", input)
    suite.addTest("println", println)
    suite.addTest("print", print)
    suite.addTest("testPlayString", testPlayString)
    suite.run()
}