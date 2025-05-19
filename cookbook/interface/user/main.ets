import {ICalculator, makeCalculator, restartCalculator} from "interface";
import {BusinessError} from "@ohos.base";

loadLibrary("interface");
function main() {
    let cal = makeCalculator(100);
    let num1 = 1;
    let num2 = 2;
    let result1 = cal.add(num1, num2);
    console.log("num1 + num2 = " + result1);
    let result2 = cal.sub(num1, num2);
    console.log("num1 - num2 = " + result2);
    let result3 = cal.getLastResult();
    console.log("Last calculation result: " + result3);
    console.log("---restart_calculator---");
    restartCalculator(cal);
    let result4 = cal.getLastResult();
    console.log("Last calculation result: " + result4);
}
