import {Option, getNumberArg4, optionArg1} from "../author_generated/ani_test"
function main() {
    console.log("hello main")
    const option: Option = {
        src: "path/to/source",
        dest: 123,
        files: ["file1.txt", "file2.txt", "file3.txt"],
    };
    console.log(getNumberArg4(1, 2, 3, 4))
    optionArg1("option1", option)
}