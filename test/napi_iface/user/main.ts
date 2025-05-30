import { makeIBase, copyIBase } from "../author_generated/iface_test";

function main() {
  let ibase_1 = makeIBase("abc");
  console.log("ibase_1 getId: ", ibase_1.getId())
  ibase_1.setId("xyz")
  console.log("ibase_1 setId: ", ibase_1.getId())
  let ibase_2 = makeIBase("test");
  copyIBase(ibase_1, ibase_2);
  console.log("copyIBase: ", ibase_1.getId(), ibase_2.getId());
}

main();
