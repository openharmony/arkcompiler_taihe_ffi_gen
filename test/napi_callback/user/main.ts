import * as lib from "cb_test";

function main() {
  lib.test_cb_v((): void => {
    console.log("test cb void success!")
  });
  lib.test_cb_i((a: number): void => {
    console.log("test cb int success! ", a)
  });
  lib.test_cb_s((a: string): void => {
    console.log("test cb string success! ", a)
  });
  lib.test_cb_rs((a: string): string => {
    console.log("test cb return string success! ")
    return "main success";
  });
  lib.test_cb_struct((data: lib.Data): lib.Data => {
    console.log("test cb return string success! ")
    return {a: "a" + data.a, b: "b" + data.b, c: 3 + data.c};
  });
  console.log(lib.test_x((): void => {
    console.log("test cb reverse success!")
  })("hello"));
}

main();
