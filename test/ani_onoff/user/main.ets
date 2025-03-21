import * as onoff_test from "../author_generated/onoff"

loadLibrary("ani_onoff")

function main() {
    let a = onoff_test.getIBase("hello", "world")
    
    try {
        a.on("set", () => {
        console.log("void input void output callback!");
    })
    } catch (error) {
        console.error("main finsih test ERROR ", error)
    }
    try {
        a.off("set", () => {
        console.log("void input void output callback!");
    })
    } catch (error) {
        console.error("main finsih test ERROR ", error)
    }
    // toplevel func on
    try {
        onoff_test.on("foo", () => {
        console.log("void input void output callback!");
    })
    } catch (error) {
        console.error("main finsih test ERROR ", error)
    }
    try {
        onoff_test.on("bar", () => {
        console.log("void input void output callback!");
    })
    } catch (error) {
        console.error("main finsih test ERROR ", error)
    }
    try {
        onoff_test.on("baz", 1, () => {
        console.log("void input void output callback!");
    })
    } catch (error) {
        console.error("main finsih test ERROR ", error)
    }

    // toplevel func off
    try {
        onoff_test.off("foo", () => {
        console.log("void input void output callback!");
    })
    } catch (error) {
        console.error("main finsih test ERROR ", error)
    }
    try {
        onoff_test.off("bar", () => {
        console.log("void input void output callback!");
    })
    } catch (error) {
        console.error("main finsih test ERROR ", error)
    }
    try {
        onoff_test.off("baz", 2, () => {
        console.log("void input void output callback!");
    })
    } catch (error) {
        console.error("main finsih test ERROR ", error)
    }

    // undefined
    try {
        onoff_test.on("ABC", () => {
        console.log("void input void output callback!");
    })
    } catch (error) {
        console.error("main finsih test ERROR ", error)
    }
    try {
        onoff_test.off("ABC", () => {
        console.log("void input void output callback!");
    })
    } catch (error) {
        console.error("main finsih test ERROR ", error)
    }
}