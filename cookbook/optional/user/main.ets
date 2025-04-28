import * as userSettings from "@generated/userSettings";
import {BusinessError} from "@ohos.base";
loadLibrary("optional");

function main() {
    // 初始化Record
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