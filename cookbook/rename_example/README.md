# Rename 重命名

> **学习目标**：掌握如何使用 `@rename` 注解修改 ArkTS 侧的函数名。

## 核心概念

`@rename` 注解用于修改函数在 ArkTS 侧的导出名称，C++ 侧仍使用原名。

| 用法 | 说明 |
|------|------|
| `@rename("newName")` | 指定新名称 |

---

## 第一步：定义接口

**File: `idl/rename_example.taihe`**

```rust
@rename("newFoo")
function oldFoo(a: i32, b: i32): i32;
```

### 生成的 ArkTS 代码

```typescript
// 不使用 @rename
export function oldFoo(a: int, b: int): int { ... }

// 使用 @rename("newFoo")
export function newFoo(a: int, b: int): int { ... }
```

## 第二步：实现 C++ 代码

**File: `author/src/rename_example.impl.cpp`**

```cpp
#include "rename_example.impl.hpp"

using namespace taihe;

// C++ 侧仍使用原名
int32_t oldFoo(int32_t a, int32_t b) {
    return a + b;
}

TH_EXPORT_CPP_API_oldFoo(oldFoo);
```

## 第三步：编译运行

```sh
taihe-tryit test -u sts cookbook/rename_example -Carkts:keep-name
```

## 使用示例

**File: `user/main.ets`**

```typescript
import * as rename_example from "rename_example";

loadLibrary("rename_example");

function main() {
    // ArkTS 侧使用新名称
    let res = rename_example.newFoo(1, 2);
    console.log("res = " + res);  // res = 3
}
```

---

## 相关文档

- [重写](../override/README.md) - 构造函数相关注解
