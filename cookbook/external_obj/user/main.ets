import * as extobj from "@generated/external_obj";

loadLibrary("external_obj");

function main() {
    console.log(extobj.is_string("hello"));
    console.log(extobj.is_string(123));

    console.log(extobj.get_objects());
}