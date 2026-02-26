# 关键字避让

> **学习目标**：掌握如何使用 `@rename` 注解修改 ArkTS 侧的投影名称。

## 核心概念

`@rename` 注解用于修改声明在 ArkTS 侧的导出名称，C++ 侧仍使用原名。

| 用法 | 适用目标 |
|------|----------|
| `@rename("newName")` | 函数、方法、enum 成员、struct 字段、enum、union、struct、interface |

> **注意：**
> - 如果 struct/interface 被 `@rename` 重命名，所有 `@ctor` 和 `@static` 的 class name 参数必须使用重命名后的名称。

#### 示例：

```rust
@class
@rename("AniRenamed")
interface AniOrigin {
    bar(): void;
}

// 正确：@ctor/@static 使用重命名后的类名
@ctor("AniRenamed")
function createAniRenamed(): AniOrigin;

@static("AniRenamed")
function staticAni(): void;

// 错误：@ctor/@static 使用原始类名会导致编译错误
// @ctor("AniOrigin")
// function createAniOrigin(): AniOrigin;
```

---

## 第一步：定义接口

**File: `idl/rename_example.taihe`**

### 函数重命名

```rust
@rename("newFoo")
function oldFoo(a: i32, b: i32): i32;
```

ArkTS 侧将生成 `newFoo`，C++ 侧仍使用 `oldFoo`。

### Enum 重命名（类型和成员）

```rust
@rename("Color")
enum OldColor: i32 {
    @rename("red") RED = 0,
    @rename("green") GREEN = 1,
    @rename("blue") BLUE = 2,
}
```

ArkTS 侧类型名为 `Color`，成员名为 `red`、`green`、`blue`。

### Struct 重命名（类型和字段）

```rust
@rename("Point")
struct OldPoint {
    @rename("xPos") x: i32;
    @rename("yPos") y: i32;
}
```

ArkTS 侧类型名为 `Point`，字段名为 `xPos`、`yPos`。

### Interface 重命名

```rust
@rename("Greeter")
interface OldGreeter {
    greet(): String;
}
```

ArkTS 侧类型名为 `Greeter`。

### 生成的 ArkTS 代码

```typescript
// 函数
export function newFoo(a: int, b: int): int { ... }

// Enum
export enum Color {
    red = 0,
    green = 1,
    blue = 2,
}

// Struct (interface + class)
export interface Point {
    xPos: int;
    yPos: int;
}

// Interface
export interface Greeter {
    greet(): string;
}
```

## 第二步：实现 C++ 代码

**File: `author/src/rename_example.impl.cpp`**

```cpp
#include "rename_example.impl.hpp"
#include "rename_example.proj.hpp"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace rename_example;

// C++ 侧仍使用原名
int32_t oldFoo(int32_t a, int32_t b) {
    return a + b;
}

OldPoint createPoint(int32_t x, int32_t y) {
    return {x, y};
}

TH_EXPORT_CPP_API_oldFoo(oldFoo);
TH_EXPORT_CPP_API_createPoint(createPoint);
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
    // 函数：ArkTS 侧使用新名称
    let res = rename_example.newFoo(1, 2);
    console.log("newFoo(1, 2) = " + res);  // 3

    // Enum：类型和成员均使用新名称
    let c: rename_example.Color = rename_example.Color.red;

    // Struct：类型和字段使用新名称
    let p = rename_example.createPoint(10, 20);
    console.log("Point.xPos = " + p.xPos);  // 10

    // Interface：类型使用新名称
    let g: rename_example.Greeter = rename_example.createGreeter("Taihe");
    console.log(g.greet());  // Hello from Taihe
}
```

---

## 相关文档

- [构造函数](../class/README.md) - 构造函数相关注解
