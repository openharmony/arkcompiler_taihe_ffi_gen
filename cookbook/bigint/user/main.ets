import {BusinessError} from "@ohos.base";
import * as bigint from "bigint";

loadLibrary("bigint");

function main() {
    let num1: BigInt = bigint.processBigInt(18446744073709551616n)
    console.log(num1)
    let num2: BigInt = bigint.processBigInt(-65535n)
    console.log(num2);
}
