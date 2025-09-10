import * as lib from "external_obj_extend";
import {Context} from "other.subsystem";

loadLibrary("external_obj_extend");

function main() {
    let context = new Context();
    console.log("base class: ", context.start(), " ", context.stop());
    let mycontext = new lib.MyContext();
    console.log("sub class: ", mycontext.start(), " ", mycontext.stop());
}