### ArrayBuffer

前面已经介绍了 基础类型 容器类型 `struct` `interface` `opaque` 类型，接下来介绍`arraybuffer`类型

<!-- 接下来介绍`optional<T>`类型和`arraybuffer`类型 -->

<!-- `optional<T>` 用于 表示可选值（可能存在，也可能不存在） -->

`arraybuffer`在Taihe中使用`array<u8>`表示

第一步 在taihe文件中声明

```taihe
function convert2Int(array<u8> a): i32;
```

第二步 实现声明的接口

```C++
// 将一段连续的byte转换成int类型
int32_t convert2Int(array_view<uint8_t> a) {
    int32_t num = 0;
    if (a.size() >= 4) { 
        num = *(int32_t*)a.begin();
    } else {
        throw_error("ArrayBuffer len < 4");
    }
    return num;
}
```

`arraybuffer`在taihe的使用与一般的`array`是一样的, 区别主要在于sts侧对应的是`ArrayBuffer`

注意到taihe提供了throw，用户在使用前需要 `#include"taihe/runtime.hpp"` , 然后就可以使用 `throw_error` 函数了

第三步 生成并编译

`compiler/`
```sh
./run-test /path/to/other_type -ani
```

用户侧使用

`main.ets`
```TypeScript
let numbersU8: byte[] = [1, 1, 0, 0, 0];
let arrbuf1: ArrayBuffer = new ArrayBuffer(numbersU8.length);
// ArrayBuffer没有length()函数
for (let i = 0; i < numbersU8.length; i++) {
    arrbuf1.set(i, numbersU8[i]);
}
let num1 = other_type.convert2Int(arrbuf1);
console.log("num1: " + num1);
// Log output：
// (小端序情况下) num1: 257

// 如果你使用下方代码
let arrbuf2: ArrayBuffer = new ArrayBuffer(3);
for (let i = 0; i < 3; i++) {
    arrbuf2.set(i, numbersU8[i]);
}
let num2 = arrbuffer.convert2Int(arrbuf2);
console.log("num2: " + num2);
// output
// [TID 09b61d] E/runtime: Error: ArrayBuffer len < 4
```