import * as StructTest from "@generated/struct_test";
import {BusinessError} from "@ohos.base";

function main() {
    let a: StructTest.A = {
        param1: 1,
    };
    let b: StructTest.B = {
        param1: 2,
        param2: 3,
    };
    let c: StructTest.C = new StructTest.C(4, 5, 6);

    console.log("a:", a);
    console.log("b:", b);
    console.log("c:", c);
}