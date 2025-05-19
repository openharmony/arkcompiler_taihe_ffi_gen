// 导入自动生成的代码
import * as hello_world from "hello_world";
import {BusinessError} from "@ohos.base";
// 加载 C++ 库
loadLibrary("hello_world");

function main() {
    let sum = hello_world.add(1, 2);
    console.log("1 + 2 = " + sum);
}
