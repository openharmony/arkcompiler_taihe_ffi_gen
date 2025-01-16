// 引入模块
const api = require('./integer');

// 定义 main 函数
function main() {
  let result = api.sub_i32(20, 2);
  console.log(result);
}

// 调用 main 函数
main();