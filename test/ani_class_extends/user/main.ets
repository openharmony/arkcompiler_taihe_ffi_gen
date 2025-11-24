import {BusinessError} from "@ohos.base";
import * as foo from "foo";

loadLibrary("ani_class_extends");

function main() {
    let data = new foo.DerivedDataClass();
    console.log(data);
    let obj = new foo.DerivedMethodClass();
    obj.base();
    obj.foo();
    obj.bar();
    obj.derived();
}
