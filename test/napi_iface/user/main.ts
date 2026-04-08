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

const lib = requireNapi('./iface_test.so', RequireBaseDir.SCRIPT_DIR);

class BaseImpl implements lib.IBase {
  id: string;
  constructor(id: string) {
    this.id = id;
  }
  getId(): string {
    return this.id;
  }
  setId(id: string): void {
    this.id = id;
    return;
  }
}

function main() {
  let ibase_1 = lib.makeIBase("abc");
  if (ibase_1.getId() !== "abc") throw new Error(`Unexpected result`);
  console.log("ibase_1 getId: ", ibase_1.getId());

  ibase_1.setId("xyz");
  if (ibase_1.getId() !== "xyz") throw new Error(`Unexpected result`);
  console.log("ibase_1 setId: ", ibase_1.getId());

  if (ibase_1.Name !== "default_base_name") throw new Error(`Unexpected result`);
  ibase_1.Name = "new_base_name";
  if (ibase_1.Name !== "new_base_name") throw new Error(`Unexpected result`);

  let ibase_2 = lib.makeIBase("test");
  lib.copyIBase(ibase_1, ibase_2);
  if (ibase_1.getId() !== ibase_2.getId()) throw new Error(`Unexpected result`);
  console.log("copyIBase: ", ibase_1.getId(), ibase_2.getId());

  let ishape_1 = lib.makeIShape("shape", 3.14, 2.5);
  console.log("makeIShape: ", ishape_1.calculateArea());
  if (ishape_1.getId() !== "shape") throw new Error(`Unexpected result`);
  console.log("interface extends: ", ishape_1.getId());

  if (ishape_1.Name !== "default_shape_name") throw new Error(`Unexpected result`);
  ishape_1.Name = "new_shape_name";
  if (ishape_1.Name !== "new_shape_name") throw new Error(`Unexpected result`);

  ishape_1.setId("aaaaa");
  if (ishape_1.getId() !== "aaaaa") throw new Error(`Unexpected result`);
  console.log("interface extends set: ", ishape_1.getId());

  let a: BaseImpl = new BaseImpl("A");
  let b: BaseImpl = new BaseImpl("B");
  lib.copyIBase(b, a);
  if (a.getId() !== b.getId()) throw new Error(`Unexpected result`);
  console.log("impl interface: ", a.getId(), b.getId());

  lib.copyIBase(ibase_1, ishape_1);
  if (ibase_1.getId() !== ishape_1.getId()) throw new Error(`Unexpected result`);
  console.log("interface extends: ", ibase_1.getId(), ishape_1.getId());

  let ctest = new lib.CTest(100);
  if (ctest.add(1, 2) !== 103) throw new Error(`Unexpected result`);
  console.log("CTets: ", ctest.add(1, 2));

  if (ctest.Id !== "default_ctest_id") throw new Error(`Unexpected result`);
  ctest.Id = "new_ctest_id";
  if (ctest.Id !== "new_ctest_id") throw new Error(`Unexpected result`);

  let new_ctest = lib.changeCTest(ctest);
  if (new_ctest.add(5, 6) !== 118) throw new Error(`Unexpected result`);
  console.log("change CTets: ", new_ctest.add(5, 6));

  let value3 = lib.CTest.multiply(7, 8);
  if (value3 !== 56) throw new Error(`Unexpected result`);
  console.log("static function: ", value3);

  let color = lib.makeIColor("my color");
  if (color.Id !== "my color") throw new Error(`Unexpected result`);
  console.log("get attr: ", color.Id);
  color.Id = "new my color";
  if (color.Id !== "new my color") throw new Error(`Unexpected result`);
  console.log("set attr: ", color.Id);
  if (color.calculate(2, 3) !== 6) throw new Error(`Unexpected result`);
  console.log("color method: ", color.calculate(2, 3))

  let d = new lib.IDerived();
  d.call();
  if (d.getId() !== "d") throw new Error(`Unexpected result`);
  console.log(d.getId());

  if (d.Name !== "default_derived_name") throw new Error(`Unexpected result`);
  d.Name = "new_derived_name";
  if (d.Name !== "new_derived_name") throw new Error(`Unexpected result`);
}

main();
