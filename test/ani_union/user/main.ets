import * as UnionTest from "../author_generated/union_ani"

loadLibrary("ani_union")

function main() {
    console.log("run main ... UnionTest ...")

    let data0 = new UnionTest.ColorName(0, undefined);
    let res = UnionTest.printUnion(data0)
    console.log(res + " ... finished")
    assertEQ(res, '0')

    let data1 = new UnionTest.ColorName(1, new UnionTest.Color(11, undefined));
    res = UnionTest.printUnion(data1)
    console.log(res + " ... finished")
    assertEQ(res, '1')

    let data2 = new UnionTest.ColorName(2, new UnionTest.RGB(1, 2, 3));
    res = UnionTest.printUnion(data2)
    console.log(res + " ... finished")
    assertEQ(res, '2')

    let data3 = new UnionTest.ColorName(3, "color");
    res = UnionTest.printUnion(data3)
    console.log(res + " ... finished")
    assertEQ(res, '3')

    let newUnion = UnionTest.makeUnion(0)
    console.log("new union is " + newUnion.tag)
    assertEQ(newUnion.tag, 0)

    newUnion = UnionTest.makeUnion(1)
    console.log("new union is " + newUnion.tag)
    assertEQ(newUnion.tag, 1)

    newUnion = UnionTest.makeUnion(2)
    console.log("new union is " + newUnion.tag)
    assertEQ(newUnion.tag, 2)

    newUnion = UnionTest.makeUnion(3)
    console.log("new union is " + newUnion.tag)
    assertEQ(newUnion.tag, 3)
}