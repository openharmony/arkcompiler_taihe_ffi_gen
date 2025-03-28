import * as basic_abilities from "../author_generated/basic_abilities";
loadLibrary("basic_abilities");
function main() {
    let input_arr: int[] = [1, 2, 3, 4, 5];
    let input_str: String = "hello";
    let output_arr: String[] =
        basic_abilities.convert_arr(input_arr, input_str);
    for (let i = 0; i < output_arr.length; i++) {
        console.log("arr [" + i + "] val " + output_arr[i])
    }
}
