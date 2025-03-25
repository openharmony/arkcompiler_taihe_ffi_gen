import * as base_test from "../author_generated/base_test"

loadLibrary("ani_basetype")

function main() {
    console.log("base_test start");
    integer_test();
    float_test();
    boolean_test();
    string_test();
    console.log("base_test end");
}

function integer_test() {
    console.log("run integer_test start ...");
    let a: byte = 2;
    let b: byte = 3;
    assertEQ(base_test.add_i8(a, b), 5);
    console.log(base_test.add_i8(a, b))

    let c: short = 2;
    let d: short = 3;
    assertEQ(base_test.sub_i16(c, d), -1);
    console.log(base_test.sub_i16(c, d))

    let e: int = 2;
    let f: int = 3;
    assertEQ(base_test.mul_i32(e, f), 6);
    console.log(base_test.mul_i32(e, f))

    let h: long = 2;
    let i: long = 2;
    assertEQ(base_test.div_i64(h, i), 1);
    console.log(base_test.div_i64(h, i))

    try {
        let x: long = 2;
        let y: long = 0;
        assertEQ(base_test.div_i64(x, y), -1);
    } catch (e) {
        console.error("divide error ...");
    }

    console.log("run integer_test end");
}

function float_test() {
    console.log("run float_test start ...");
    let a: float = 2.5;
    let b: float = 3.5;
    let c: float = base_test.add_f32(a, b);
    assertEQ(c, 6.0);
    console.log(
        "add_f32 result : " +
            `ret = `,
        c);

    let d: float = 4.3;
    let e: float = 3.0;
    let f: float = base_test.sub_f32(d, e);
    assertEQ(f >= 1.3, true);
    console.log(
        "sub_f32 result : " +
            `ret = `,
        f);

    let h: float = 3.7;
    let i: double = 5.3;
    let j: double = base_test.add_f64(h, i);
    assertEQ(j >= 9.0, true);
    console.log(
        "add_f64 result : " +
            `ret = `,
        j);

    let k: float = 3.5;
    let l: double = 1.0;
    let m: double = base_test.sub_f64(k, l);
    assertEQ(m >= 2.5, true);
    console.log(
        "sub_f64 result : " +
            `ret = `,
        m);

    let x: float = 2.5;
    let y: float = 4.0;
    let z: double = base_test.mul_f64(x, y);
    assertEQ(z, 10.0);
    console.log(
        "mul_f64 result : " +
            `ret = `,
        z);
    console.log("run float_test end");
}

function boolean_test() {
    console.log("run boolean_test start ...");
    let a = true;
    let b = true;
    assertEQ(base_test.check(a, b), true);
    a = true;
    b = false;
    assertEQ(base_test.check(a, b), false);
    a = false;
    b = true;
    assertEQ(base_test.check(a, b), false);
    a = false;
    b = false;
    assertEQ(base_test.check(a, b), false);
    console.log("run boolean_test end");
}

function string_test() {
    console.log("run string_test start ...");
    let a: string = "tai";
    let b: string = "he";
    assertEQ(base_test.concatx(a, b), "taihe");

    let c: string = "taihe";
    assertEQ(base_test.splitx(c, 3), "tai");

    let d: string = "10";
    assertEQ(base_test.to_i32(d), 10);

    let e: int = 10;
    assertEQ(base_test.from_i32(e), "10");

    console.log("run string_test end");
}
