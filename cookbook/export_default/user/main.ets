import {BusinessError} from "@ohos.base";
import export_ns from "export_pkg";
import {testImport} from "import_example";

loadLibrary("export_default");

function main() {
    let obj: export_ns.Inner = {i: 1, s: "str"};
    testImport(obj);
}
