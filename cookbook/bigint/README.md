# BigInt

> **学习目标**：掌握 Taihe 中 BigInt 类型的定义与使用。

## 核心概念

| Taihe 表示 | ArkTS 类型 | C++ 类型 |
|------------|------------|----------|
| `@bigint Array<u64>` | `BigInt` | `array<uint64_t>` / `array_view<uint64_t>` |

> **注意**：`@bigint` 注解只能用于 `Array<u64>` 类型。

---

## 第一步：定义接口

**File: `idl/bigint.taihe`**

```rust
function processBigInt(a: @bigint Array<u64>): @bigint Array<u64>;
```

### 类型注解说明

由于 ArkTS 没有无符号数组的直接支持，`Array<uxx>` 类型需要显式添加注解：

| 注解 | 适用类型 | ArkTS 对应类型 |
|------|----------|----------------|
| `@bigint` | `Array<u64>` | `BigInt` |
| `@arraybuffer` | `Array<u8>` | `ArrayBuffer` |
| `@typedarray` | 所有 `Array<T>` | 对应的 TypedArray |

## 第二步：实现 C++ 代码

**File: `author/src/bigint.impl.cpp`**

```cpp
#include "bigint.impl.hpp"

using namespace taihe;

// 将输入的 BigInt 左移 64 位
array<uint64_t> processBigInt(array_view<uint64_t> a) {
    array<uint64_t> result(a.size() + 1);
    result[0] = 0;  // 最低位补 0
    for (std::size_t i = 0; i < a.size(); i++) {
        result[i + 1] = a[i];
        std::cerr << "arr[" << i << "] = " << a[i] << std::endl;
    }
    return result;
}

TH_EXPORT_CPP_API_processBigInt(processBigInt);
```

## 第三步：编译运行

```sh
taihe-tryit test -u sts cookbook/bigint
```

## 使用示例

**File: `user/main.ets`**

```typescript
import * as bigint from "bigint";

loadLibrary("bigint");

function main() {
    // 处理正数 BigInt
    let num1 = bigint.processBigInt(18446744073709551616n);
    console.log(num1);
    // 输出: 340282366920938463463374607431768211456
    
    // 处理负数 BigInt
    let num2 = bigint.processBigInt(-65535n);
    console.log(num2);
}
```

**输出：**

```
arr[0] = 0
arr[1] = 1
340282366920938463463374607431768211456
arr[0] = 18446744073709486081
-1208907372870555465154560
```

---

## 相关文档

- [TypedArray](../typedarray/README.md) - TypedArray 类型
- [ArrayBuffer](../arraybuffer/README.md) - ArrayBuffer 类型
