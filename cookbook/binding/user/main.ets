import * as binding from "../author_generated/binding"
loadLibrary("binding")
function main() {
    let Color1: binding.Color = {R: 0, G: 255, B: 255};
    console.log("Color1 is " + Color1.R + " " + Color1.G + " " + Color1.B)
    let Color2 = binding.convert_color(Color1)
    console.log("Color2 is " + Color2.R + " " + Color2.G + " " + Color2.B)
}