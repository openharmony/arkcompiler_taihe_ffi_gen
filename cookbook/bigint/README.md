# BigInt

taihe 使用增加 `@bigint` 注解的方式支持 `BigInt`

## 第一步：编写接口原型

**File: `idl/bigint.taihe`**
```rust
function processBigInt(a: @bigint Array<u64>): @bigint Array<u64>;
```

因为 sts 没有无符号 array 的支持，`Array\<uxx\>` 类型需要显式增加注解才能使用，如果不显式增加注解则无法正常使用

我们可以发现该注解是增加给类型的，也就是在类型前添加注解，同类的注解还有 `@arraybuffer` 以及 `@typedarray`, `@arraybuffer` 只能给 `Array<\u8\>` 增加注解，`@bigint` 只能给 `Array<\u64\>` 增加注解，`@typedarray` 可以给所有的 `array` 类型增加注解，该类注解的作用是，在 sts 层与注解对应类型桥接起来

## 第二步：完成 C++ 实现

array<uint64_t> processBigInt(array_view<uint64_t> a) {
    array<uint64_t> res(a.size() + 1);
    res[0] = 0;
    for (std::size_t i = 0; i < a.size(); i++) {
      res[i + 1] = a[i];
      std::cerr << "arr[" << i << "] = " << a[i] << std::endl;
    }
    return res;
}

该函数逻辑为将输入的 bigint 左移 64 位，并将原输入以 uint64_t 输出

## 第三步：在 ets 侧使用

```typescript
let num1: BigInt = bigint.processBigInt(18446744073709551616n)
console.log(num1)
let num2: BigInt = bigint.processBigInt(-65535n)
console.log(num2);
```

Output:
```sh
arr[0] = 0
arr[1] = 1
340282366920938463463374607431768211456
arr[0] = 18446744073709486081
-1208907372870555465154560
```