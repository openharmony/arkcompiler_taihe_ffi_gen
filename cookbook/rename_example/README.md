# 名称重定义与关键字避让

> **学习目标**：掌握如何使用 `@rename` 注解修改目标端（如 ArkTS 侧）的投影名称，以及如何使用 `#` 标识符实现关键字避让。

## 场景与目的

在跨语言绑定中，不同语言对关键字和重载的规则不同。Taihe 提供了 `@rename` 和 `#` 机制来对标识符名称进行映射与隔离，主要解决两类需求：

1. **实现函数重载**：Taihe IDL 和 C 语言不支持同名重载（同名不同参），但在 ArkTS 等应用侧能够支持。通过给签名不同但逻辑上属于重载的一组函数指定相同的 `@rename("name")` 名称，这组函数可以在支持重载的目标语言（比如 ArkTS）中统一暴露为相同的名，实现函数重载的效果。
2. **实现关键字或宏避让**：
   - **目标语言内建宏/关键字冲突（使用 `@rename`）**：比如 `NULL` 是 C/C++ 常用的宏。若直接在 Taihe 内声明 `NULL` 这个名称，可能会导致生成的 C++ 代码编译出错。此时可以使用一个安全的内部名（如 `fieldNULL`），并使用 `@rename("NULL")` 在映射到 ArkTS 时改回 `NULL` 从而规避目标语言保留字的语法冲突。
   - **Taihe 关键字冲突（使用 `#` 转义）**：如果有需要在接口里使用 Taihe 语言自带的关键字作为参数或方法名（如 `use`, `from`），可以通过加上 `#`（如 `#use`）转义。Taihe 内部仅视其为普通的标识符而不在生成代码里引入 `#` 字符。

---

## 机制详解与示例

### 1. `@rename` 注解

`@rename` 用于修改特定节点在目标语言（如 ArkTS）对应的导出名称，而底层（如 C++ 侧）由于不支持或未修改将仍使用原名称。

| 用法 | 适用目标 |
|------|----------|
| `@rename("newName")` | 函数、方法、enum 成员、struct 字段、enum、union、struct、interface |

> **注意：**
> - 如果 struct/interface 被 `@rename` 重命名，相关的所有 `@ctor` 和 `@static` 的 `class name` 参数中必须使用重命名后的新名称。

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
