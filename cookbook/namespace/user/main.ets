import {BusinessError} from "@ohos.base";
import * as Module1 from "module1";
import * as Module2 from "module2";

loadLibrary("namespace");

function main() {
    Module1.module1Run();
    Module1.foo.fooFunc();
    Module2.bar.barFunc();
}