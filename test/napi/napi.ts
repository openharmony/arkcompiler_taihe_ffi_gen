// 引入模块
const api = require('./integer');

// 定义 main 函数
function main() {
  let result1 = api.mul(20, 2);
  console.log(result1);
  let result2 = api.add(20, 2);
  console.log(result2);
}

// 调用 main 函数
main();