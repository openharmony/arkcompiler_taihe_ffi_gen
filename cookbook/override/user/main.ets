import {BusinessError} from "@ohos.base";
import {UIAbility, useUIAbility} from "override";

loadLibrary("override");

class MyAbility extends UIAbility {
    constructor() {
        super();
    }
    onForeground(): void {
        console.log("in ets onForeground")
    }
}

function main() {
    let my_uiability: UIAbility = new MyAbility();
    useUIAbility(my_uiability);
    MyAbility.logLifecycle("using uiability")
}