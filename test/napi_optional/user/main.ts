import { showOptionalInt, makeOptionalInt } from "opt_test";

function main() {
  showOptionalInt(1);
  showOptionalInt(undefined);
  let res1 = makeOptionalInt(true);
  console.log(res1);
  let res2 = makeOptionalInt(false);
  console.log(res2);
}

main();
