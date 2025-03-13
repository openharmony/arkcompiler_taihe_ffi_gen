import * as ani_test from "../author_generated/ani_test"
function main() {
    console.log("hello main")
    console.log(ani_test.getNumberArg4(1, 2, 3, 4))

    const option: ani_test.Option = new ani_test.Option(
        "path/to/source",
        123,
        ["file1.txt", "file2.txt", "file3.txt"]
    )
    ani_test.optionArg1("option1", option)

    console.log(ani_test.getOption())

    ani_test.testUnion(new ani_test.Union(0, undefined))
    ani_test.testUnion(new ani_test.Union(1, 1 as int))
    ani_test.testUnion(new ani_test.Union(2, 2 as float))
    ani_test.testUnion(new ani_test.Union(3, "Hello from STS!"))

    console.log(ani_test.getUnion(0))
    console.log(ani_test.getUnion(1))
    console.log(ani_test.getUnion(2))
    console.log(ani_test.getUnion(3))

    ani_test.testOptionalDouble(3.0 as double)
}
