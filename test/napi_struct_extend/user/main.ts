/*
 * Copyright (c) 2025 Huawei Device Co., Ltd.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

const lib = requireNapi('./struct_extend.so', RequireBaseDir.SCRIPT_DIR);

class C implements lib.C {
    param1: number = 100;
    param2: number = 200;
    param3: number = 300;
}

function main() {
    let ins_a: lib.A = {param1: 100};
    lib.check_A(ins_a);
    let res_a = lib.create_A();
    if (res_a.param1 !== 1) throw new Error(`Unexpected result`);
    console.log("create_A: ", res_a.param1);

    let ins_b: lib.B = {param1: 100, param2: 200};
    lib.check_B(ins_b)
    let res_b = lib.create_B()
    if (res_b.param1 !== 1 && res_b.param2 !== 2) throw new Error(`Unexpected result`);
    console.log("create_B: ", res_b.param1, res_b.param2);

    let ins_c: lib.C = new C();
    lib.check_C(ins_c);
    let res_c = lib.create_C();
    if (res_c.param1 !== 1 && res_c.param2 !== 2 && res_c.param3 !== 3) throw new Error(`Unexpected result`);
    console.log("check_C: ", res_c.param1, res_c.param2, res_c.param3);

    let ins_d: lib.D = {param4: 400};
    lib.check_D(ins_d);
    let res_d = lib.create_D();
    if (res_d.param4 !== 4) throw new Error(`Unexpected result`);
    console.log("check_D: ", res_d.param4);

    let ins_e: lib.E = {param4: 400, param5: 500};
    lib.check_E(ins_e);
    let res_e = lib.create_E();
    if (res_e.param4 !== 4 && res_e.param5 !== 5) throw new Error(`Unexpected result`);
    console.log("create_E: ", res_e.param4, res_e.param5);

    let in_e: lib.E = {param4: 4, param5: 5};
    let bar: lib.Bar = lib.create_Bar(in_e);
    if (!lib.check_Bar(bar)) throw new Error(`Unexpected result`);
    console.log("check_Bar: ", lib.check_Bar(bar));
    let e: lib.E = bar.getE();
    if (e.param4 !== 4 && e.param5 !== 5) throw new Error(`Unexpected result`);
    console.log("bar.getE: ", e.param4, e.param5);
    let e1: lib.E = {param4: 400, param5: 500};
    bar.setE(e1);
    let e2: lib.E = bar.getE();
    if (e2.param4 !== 400 && e2.param5 !== 500) throw new Error(`Unexpected result`);
    console.log("bar.setE: ", e2.param4, e2.param5);

    let f: lib.F = lib.create_F(in_e);
    if (!lib.check_F(f)) throw new Error(`Unexpected result`);
    console.log("check_F: ", lib.check_F(f));
    let new_e: lib.E = f.barF.getE();
    if (new_e.param4 !== 4 && new_e.param5 !== 5) throw new Error(`Unexpected result`);
    console.log("f.barF.getE: ", new_e.param4, new_e.param5);

    let g = lib.create_G(in_e);
    if (!lib.check_F(g)) throw new Error(`Unexpected result`);
    console.log("check_F: ", lib.check_F(g));
    let new_e1: lib.E = g.barF.getE();
    if (new_e1.param4 !== 4 && new_e1.param5 !== 5) throw new Error(`Unexpected result`);
    console.log("g.barF.getE: ", new_e1.param4, new_e1.param5);
    let new_e2: lib.E = g.barG.getE();
    if (new_e2.param4 !== 4 && new_e2.param5 !== 5) throw new Error(`Unexpected result`);
    console.log("g.barG.getE: ", new_e2.param4, new_e2.param5);
}

main();
