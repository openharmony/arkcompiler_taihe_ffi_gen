import * as lib from "iface_test";

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
  console.log("ibase_1 getId: ", ibase_1.getId());

  ibase_1.setId("xyz");
  console.log("ibase_1 setId: ", ibase_1.getId());

  let ibase_2 = lib.makeIBase("test");
  lib.copyIBase(ibase_1, ibase_2);
  console.log("copyIBase: ", ibase_1.getId(), ibase_2.getId());

  let ishape_1 = lib.makeIShape("shape", 3.14, 2.5);
  console.log("makeIShape: ", ishape_1.calculateArea());
  console.log("interface extends: ", ishape_1.getId());

  ishape_1.setId("aaaaa");
  console.log("interface extends set: ", ishape_1.getId());

  let a: BaseImpl = new BaseImpl("A");
  let b: BaseImpl = new BaseImpl("B");
  lib.copyIBase(b, a);
  console.log("impl interface: ", a.getId(), b.getId());

  lib.copyIBase(ibase_1, ishape_1);
  console.log("interface extends: ", ibase_1.getId(), ishape_1.getId());

  let ctest = new lib.CTest(100);
  console.log("CTets: ", ctest.add(1, 2));

  let new_ctest = lib.changeCTest(ctest);
  console.log("change CTets: ", new_ctest.add(5, 6));

  let value3 = lib.CTest.multiply(7, 8);
  console.log("static function: ", value3);

  let color = lib.makeIColor("my color");
  console.log("get attr: ", color.Id);
  color.Id = "new my color";
  console.log("set attr: ", color.Id);
  console.log("color method: ", color.calculate(2, 3))
}

main();
