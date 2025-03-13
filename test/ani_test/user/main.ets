import * as ani_test from "../author_generated/ani_test"
function main() {
    console.log("hello main")
    const option: ani_test.Option = {
        src: "path/to/source",
        dest: 123,
        files: ["file1.txt", "file2.txt", "file3.txt"],
    };
    console.log(ani_test.getNumberArg4(1, 2, 3, 4))
    ani_test.optionArg1("option1", option)
}