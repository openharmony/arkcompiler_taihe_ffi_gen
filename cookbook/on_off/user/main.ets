import * as OnOff from "@generated/on_off";
import {BusinessError} from "@ohos.base";

loadLibrary("on_off");

function main() {
    let num0: Int = 0;
    let num1: Int = 1;
    let obj = OnOff.getISetterObserver();
    obj.on("set", (): void => {
        console.log("ISetterObserver onSet callback");
    });
    obj.off("set", (): void => {
        console.log("ISetterObserver offSet callback");
    });
    OnOff.on("foo", (): void => {
        console.log("onFoo callback");
    });
    OnOff.on("bar", (): void => {
        console.log("onBar callback");
    });
    OnOff.on("newBaz", num1, (arg0: Int): void => {
        console.log("onNewBaz callback, num: " + arg0);
    });
    OnOff.off("foo", (): void => {
        console.log("offFoo callback");
    });
    OnOff.off("bar", (): void => {
        console.log("offBar callback");
    });
    OnOff.off("newBaz", num0, (arg0: Int): void => {
        console.log("offNewBaz callback, num: " + arg0);
    });
}