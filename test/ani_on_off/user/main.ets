import * as on_off_test from "../author_generated/on_off"

loadLibrary("ani_on_off")

function main() {
    let a = on_off_test.getIBase("hello", "world")

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
        on_off_test.on("foo", () => {
            console.log("void input void output callback!");
        })
    } catch (error) {
        console.error("main finsih test ERROR ", error)
    }
    try {
        on_off_test.on("bar", () => {
            console.log("void input void output callback!");
        })
    } catch (error) {
        console.error("main finsih test ERROR ", error)
    }
    try {
        on_off_test.on("my_baz", 1, () => {
            console.log("void input void output callback!");
        })
    } catch (error) {
        console.error("main finsih test ERROR ", error)
    }

    // toplevel func off
    try {
        on_off_test.off("foo", () => {
            console.log("void input void output callback!");
        })
    } catch (error) {
        console.error("main finsih test ERROR ", error)
    }
    try {
        on_off_test.off("bar", () => {
            console.log("void input void output callback!");
        })
    } catch (error) {
        console.error("main finsih test ERROR ", error)
    }
    try {
        on_off_test.off("my_baz", 2, () => {
            console.log("void input void output callback!");
        })
    } catch (error) {
        console.error("main finsih test ERROR ", error)
    }

    // undefined
    try {
        on_off_test.on("ABC", () => {
            console.log("void input void output callback!");
        })
    } catch (error) {
        console.error("main finsih test ERROR ", error)
    }
    try {
        on_off_test.off("ABC", () => {
            console.log("void input void output callback!");
        })
    } catch (error) {
        console.error("main finsih test ERROR ", error)
    }
}