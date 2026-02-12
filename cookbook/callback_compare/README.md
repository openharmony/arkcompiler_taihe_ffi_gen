# Callback 对象比较

> **学习目标**：掌握如何在 C++ 中比较两个 callback 对象是否相等。

## 核心概念

Taihe 支持 callback 对象的判等比较，在 C++ 侧使用 `==` 运算符。

---

## 第一步：定义接口

**File: `idl/cb_compare.taihe`**

```rust
function cbCompare(cb1: () => String, cb2: () => String): bool;
```

## 第二步：实现 C++ 代码

**File: `author/src/cb_compare.impl.cpp`**

```cpp
#include "cb_compare.impl.hpp"

using namespace taihe;

bool cbCompare(callback_view<string()> cb1, callback_view<string()> cb2) {
    return cb1 == cb2;  // 直接使用 == 比较
}

TH_EXPORT_CPP_API_cbCompare(cbCompare);
```

## 第三步：编译运行

```sh
taihe-tryit test -u sts cookbook/cb_compare
```

## 使用示例

**File: `user/main.ets`**

```typescript
import { cbCompare } from "cb_compare";

loadLibrary("cb_compare");

function main() {
    let callback_1 = () => {
        console.log("Callback 1 executed");
        return "Callback 1 result";
    };
    
    let callback_2 = () => {
        console.log("Callback 2 executed");
        return "Callback 2 result";
    };
    
    // 相同 callback 比较
    console.log("same: " + cbCompare(callback_1, callback_1));     // true
    
    // 不同 callback 比较
    console.log("different: " + cbCompare(callback_1, callback_2)); // false
}
```

**输出：**

```
same: true
different: false
```

---

## 相关文档

- [Callback 回调](../callback/README.md) - 回调函数基础
- [Taihe C++](../taihe_cpp/README.md) - C++ API 参考
