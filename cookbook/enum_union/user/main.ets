import * as message from "@generated/message";
import {BusinessError} from "@ohos.base";
loadLibrary("enum_union");
function main() {
    // 创建文本信息
    let textMsg = message.createTextMessage("hello");
    // 创建数字信息
    let numMsg = message.createNumberMessage(12345);
    // 输出信息
    message.processMessage(textMsg);
    message.processMessage(numMsg);
}