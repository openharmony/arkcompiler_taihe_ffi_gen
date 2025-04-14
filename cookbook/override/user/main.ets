import {UIAbility, useUIAbility} from "@generated/override";

loadLibrary("override");

function main() {
    class MyAbility extends UIAbility {
        constructor() {
            super();
        }
        onForeground(): void {
            console.log("in ets onForeground")
        }
    }
    let my_uiability: UIAbility = new MyAbility();
    useUIAbility(my_uiability);
    MyAbility.logLifecycle("using uiability")
}