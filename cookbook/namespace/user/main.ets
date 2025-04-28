import * as Module1 from "@generated/module1";
import * as Module2 from "@generated/module2";
import {BusinessError} from "@ohos.base";

loadLibrary("namespace");

function main() {
    Module1.module1Run();
    Module1.foo.fooFunc();
    Module2.bar.barFunc();
}