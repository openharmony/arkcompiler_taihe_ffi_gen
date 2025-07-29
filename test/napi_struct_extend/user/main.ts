import * as lib from "struct_extend";

class C implements lib.C {
    param1: number = 100;
    param2: number = 200;
    param3: number = 300;
}

function main() {
    let ins_a: lib.A = {param1: 100};
    lib.check_A(ins_a);
    let res_a = lib.create_A();
    console.log("create_A: ", res_a.param1);

    let ins_b: lib.B = {param1: 100, param2: 200};
    lib.check_B(ins_b)
    let res_b = lib.create_B()
    console.log("create_B: ", res_b.param1, res_b.param2);

    let ins_c: lib.C = new C();
    lib.check_C(ins_c);
    let res_c = lib.create_C();
    console.log("check_C: ", res_c.param1, res_c.param2, res_c.param3);

    let ins_d: lib.D = {param4: 400};
    lib.check_D(ins_d);
    let res_d = lib.create_D();
    console.log("check_D: ", res_d.param4);

    let ins_e: lib.E = {param4: 400, param5: 500};
    lib.check_E(ins_e);
    let res_e = lib.create_E();
    console.log("create_E: ", res_e.param4, res_e.param5);

    let in_e: lib.E = {param4: 4, param5: 5};
    let bar: lib.Bar = lib.create_Bar(in_e);
    console.log("check_Bar: ", lib.check_Bar(bar));
    let e: lib.E = bar.getE();
    console.log("bar.getE: ", e.param4, e.param5);
    let e1: lib.E = {param4: 400, param5: 500};
    bar.setE(e1);
    let e2: lib.E = bar.getE();
    console.log("bar.setE: ", e2.param4, e2.param5);

    let f: lib.F = lib.create_F(in_e);
    console.log("check_F: ", lib.check_F(f));
    let new_e: lib.E = f.barF.getE();
    console.log("f.barF.getE: ", new_e.param4, new_e.param5);

    let g = lib.create_G(in_e);
    console.log("check_F: ", lib.check_F(g));
    let new_e1: lib.E = g.barF.getE();
    console.log("g.barF.getE: ", new_e1.param4, new_e1.param5);
    let new_e2: lib.E = g.barG.getE();
    console.log("g.barG.getE: ", new_e2.param4, new_e2.param5);
}

main();
