import * as container_example from "../author_generated/container_example"
loadLibrary("container_example")
function main() {
    let input_arr: int[] = [1, 2, 3, 4, 5]
    let output_arr: int[] = container_example.convert_arr(input_arr)
    for (let i = 0; i < output_arr.length; i++) {
        console.log("arr " + i + " val " + output_arr[i])
    }
}