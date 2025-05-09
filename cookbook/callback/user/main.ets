import * as callback_lib from "@generated/callback";
import {BusinessError} from "@ohos.base";

loadLibrary("callback");

function main() {
    callback_lib.cb_void_void(() => {
        console.log("void input void output callback!");
    });
    callback_lib.cb_i_void((a: int) => {
        console.log("int input void output callback! input is: ", a);
    });
    let result = callback_lib.cb_str_str((a: string) => {
        console.log("param a is: ", a);
        return "my return value";
    });
    console.log("global function output: ", result);
    callback_lib.cb_struct((a: callback_lib.Person) => {
        let person: callback_lib.Person = {
            name: (a.name + " Swift"),
            age: (a.age + 18)
        };
        return person;
    });
}
