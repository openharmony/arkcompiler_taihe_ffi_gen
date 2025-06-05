import { test_cb_v, test_cb_i, test_cb_s, test_cb_rs, test_cb_struct, Data } from "../generated/cb_test";

function main() {
  test_cb_v((): void => {
    console.log("test cb void success!")
  });
  test_cb_i((a: number): void => {
    console.log("test cb int success! ", a)
  });
  test_cb_s((a: string): void => {
    console.log("test cb string success! ", a)
  });
  test_cb_rs((a: string): string => {
    console.log("test cb return string success! ")
    return "main success";
  });
  test_cb_struct((data: Data): Data => {
    console.log("test cb return string success! ")
    return {a: "a" + data.a, b: "b" + data.b, c: 3 + data.c};
  });
}

main();
