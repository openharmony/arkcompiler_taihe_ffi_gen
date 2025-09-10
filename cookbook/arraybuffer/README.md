# ArrayBuffer

前面已经介绍了基础类型，容器类型，`struct`，`interface`，`opaque`，类型，接下来介绍 `ArrayBuffer` 类型。

`ArrayBuffer` 在 Taihe 中使用 `@arraybuffer Array<u8>` 表示。

## 第一步：在 Taihe IDL 文件中声明

```rust
function convert2Int(a: @arraybuffer Array<u8>): i32;
```

## 第二步：实现声明的接口

```cpp
// 将一段连续的 byte 转换成 int 类型
int32_t convert2Int(array_view<uint8_t> a) {
    int32_t num = 0;
    if (a.size() >= 4) { 
        num = *(int32_t*)a.begin();
    } else {
        set_business_error(1, "ArrayBuffer len < 4");
    }
    return num;
}
```

`ArrayBuffer` 在 taihe C++ 实现侧的使用与一般的 `Array<T>` 是一样的，区别主要在于 sts 侧对应的是 `ArrayBuffer`

## 第三步：生成并编译

```sh
# 注：Taihe IDL 文件里的函数与 C++ 规范一致，所以函数会在生成的 ets 侧自动转变为小写字母开头函数
# Taihe IDL 文件中的写法：
#   function FooBar(): void;
# 生成的 ets 侧代码
#   function fooBar(): void;
# 如果希望生成的 ets 侧函数与 Taihe IDL 文件一致，可以使用 -Csts:keep-name
taihe-tryit test -u sts path/to/arraybuffer -Csts:keep-name
```

## 用户侧使用

`main.ets`
```typescript
let numbersU8: byte[] = [1, 1, 0, 0, 0];
let arrbuf1: ArrayBuffer = new ArrayBuffer(numbersU8.length);
for (let i = 0; i < numbersU8.length; i++) {
    arrbuf1.set(i, numbersU8[i]);
}
let num1 = other_type.convert2Int(arrbuf1);
console.log("num1: " + num1);
// Log output：
// num1: 257

// 如果你使用下方代码
let arrbuf2: ArrayBuffer = new ArrayBuffer(3);
for (let i = 0; i < 3; i++) {
    arrbuf2.set(i, numbersU8[i]);
}
let num2 = arraybuffer.convert2Int(arrbuf2);
console.log("num2: " + num2);
// [TID 09b61d] E/runtime: Error: ArrayBuffer len < 4
```