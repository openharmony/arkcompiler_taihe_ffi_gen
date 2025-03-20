import * as UnionTest from "../author_generated/union_ani"

loadLibrary("ani_union")

function main() {
    console.log("run main ... UnionTest ...")

    let res: string;

    res = UnionTest.printUnion(undefined)
    console.log(res);

    res = UnionTest.printUnion("name")
    console.log(res)

    res = UnionTest.printUnion(123)
    console.log(res)

    res = UnionTest.printUnion(new UnionTest.Pair("a", "b"))
    console.log(res)

    console.log(UnionTest.makeUnion("s"))
    console.log(UnionTest.makeUnion("i"))
    console.log(UnionTest.makeUnion("p"))
    console.log(UnionTest.makeUnion("u"))
}
