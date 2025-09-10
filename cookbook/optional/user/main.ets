import {BusinessError} from "@ohos.base";
import * as userSettings from "userSettings";

loadLibrary("optional");

function main() {
    // 初始化 Record
    let Settings: Record<string, string> = {
        "theme": "dark",
        "fontSize": "14px",
        "language": "en-US",
    };
    // 查找设置
    let setting1 = userSettings.getUserSetting(Settings, "theme");
    let setting2 = userSettings.getUserSetting(Settings, "autosave");
    console.log("theme: " + setting1);
    console.log("autosave: " + setting2);
}