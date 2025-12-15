import {BusinessError} from "@ohos.base";
import * as foo from "foo";

loadLibrary("ani_class_extends");

function check_struct_class_extend() {
    let data = foo.makeDerivedDataClass();
    arktest.assertEQ(data.a, "base");
    arktest.assertEQ(data.p, "foo");
    arktest.assertEQ(data.q, "bar");
    arktest.assertEQ(data.x, 42);
    arktest.assertEQ(data.y, 56);
}

function check_interface_class_extend() {
    let obj = new foo.DerivedMethodClass();
    arktest.assertEQ(obj.base(), "base");
    arktest.assertEQ(obj.foo(), "foo");
    arktest.assertEQ(obj.bar(), "bar");
    arktest.assertEQ(obj.derived(), "derived");
}

function main() {
    const suite = new arktest.ArkTestsuite("class extend ut")
    suite.addTest("check struct class extend", check_struct_class_extend)
    suite.addTest("check interface class extend", check_interface_class_extend)
    exit(suite.run())
}
