import * as extobj from "../author_generated/external_obj";

loadLibrary("external_obj");

function main() {
    console.log(extobj.is_string("hello"));
    console.log(extobj.is_string(undefined));

    console.log(extobj.get_objects());
}