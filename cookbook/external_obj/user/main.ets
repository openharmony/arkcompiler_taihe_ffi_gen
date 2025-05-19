import {BusinessError} from "@ohos.base";
import * as extobj from "external_obj";
import {Person} from "other.subsystem";

loadLibrary("external_obj");

function main() {
    console.log(extobj.is_string("hello"));
    console.log(extobj.is_string(123));

    let person: Person = {name: "John", age: 30};

    extobj.processPerson(person);

    console.log(extobj.get_objects());
}