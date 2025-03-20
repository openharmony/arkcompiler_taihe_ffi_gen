import * as lib from "../author_generated/callbackTest"

loadLibrary("ani_callback")

function main() {
    lib.test_cb_v(() => {
        console.log("void input void output callback!");
    });
    lib.test_cb_i((a: int) => {
        console.log("int input void output callback! input is: ", a);
    });
    lib.test_cb_s((a: string, b: boolean) => {
        if (b) {
            console.log("param b is true and param a is: ", a);
        } else {
            console.log("param b is false");
        }
    });
    let result = lib.test_cb_rs((a: string) => {
        console.log("param a is: ", a);
        return "my return value";
    });
    console.log("global function output: ", result);
    lib.test_cb_struct((a: lib.Data) => {
        let data = new lib.Data(a.a + "main", a.b + "main", a.c + 100 ); 
        return data;
    });
}
