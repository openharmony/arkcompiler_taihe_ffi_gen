import * as lib from "../generated/bigint_test";

function main() {
    let num1: bigint = lib.processBigInt(18446744073709556846815135465465564525825546451551616n);
    console.log(num1);
    let num2: bigint = lib.processBigInt(-65535n);
    console.log(num2);
}

main()
