import { makeIBase, copyIBase, makeIShape, IBase } from "../generated/iface_test";

class BaseImpl implements IBase {
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
  let ibase_1 = makeIBase("abc");
  console.log("ibase_1 getId: ", ibase_1.getId())
  ibase_1.setId("xyz")
  console.log("ibase_1 setId: ", ibase_1.getId())
  let ibase_2 = makeIBase("test");
  copyIBase(ibase_1, ibase_2);
  console.log("copyIBase: ", ibase_1.getId(), ibase_2.getId());
  let ishape_1 = makeIShape("shape", 3.14, 2.5);
  console.log("makeIShape: ", ishape_1.calculateArea());
  console.log("interface extends: ", ishape_1.getId());
  ishape_1.setId("aaaaa")
  console.log("interface extends set: ", ishape_1.getId());
  let a: BaseImpl = new BaseImpl("A");
  let b: BaseImpl = new BaseImpl("B");
  copyIBase(b, a);
  console.log("impl interface", a.getId(), b.getId());
}

main();
