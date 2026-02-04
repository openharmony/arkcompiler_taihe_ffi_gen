# Struct 继承

> **学习目标**：掌握如何通过 `@extends` 注解实现 struct 的组合式继承。

## 核心概念

Taihe 的 `struct` 是值类型，不支持传统继承。通过 `@extends` 注解，可以用组合的方式实现类似继承的效果。

| 注解 | 作用 |
|------|------|
| `@extends` | 将成员 struct 的字段展开到父级 |
| `@class` | struct 直接生成为 class（而非 interface + class_inner） |

### struct 与 interface 继承方式对比

| 类型 | 继承语法 | 适用场景 |
|------|----------|----------|
| `interface` | `interface Derived: Base { }` | 带方法的接口 |
| `struct` | `struct Derived { @extends base: Base; }` | 纯数据类型 |

> **重要**：只允许 interface 与 interface 之间、struct 与 struct 之间继承，**不允许** interface 和 struct 之间继承/实现。

### TypeScript 到 Taihe 的转换

**纯数据接口：**

```typescript
// TypeScript
interface BaseDataInterface {
    id: string;
}

interface DerivedDataInterface extends BaseDataInterface {
    value: number;
}
```

转换为：

```rust
// Taihe
struct BaseDataInterface {
    id: String;
}

struct DerivedDataInterface {
    @extends base: BaseDataInterface;
    value: i32;
}
```

带方法的接口继承请参见 [继承](../inherit/README.md)。

---

## 第一步：定义接口

**File: `idl/structext.taihe`**

```rust
struct Position {
    x: i32;
    y: i32;
    z: i32;
}

@class
struct Player {
    @extends pos: Position;  // 组合式继承
    name: String;
}

function addNewPlayer(name: String): Player;
```

### 生成的 ArkTS 代码

```typescript
export class Player implements Position {
    x: int;      // 从 Position 展开
    y: int;
    z: int;
    name: string;
    
    constructor(x: int, y: int, z: int, name: string) {
        this.x = x;
        this.y = y;
        this.z = z;
        this.name = name;
    }
}
```

> **说明**：使用 `@extends` 后，`Position` 的字段直接展开到 `Player` 中，访问时使用 `player.x` 而非 `player.pos.x`。

## 第二步：实现 C++ 代码

**File: `author/src/structext.impl.cpp`**

```cpp
#include "structext.impl.hpp"

using namespace taihe;

Player addNewPlayer(string_view name) {
    // 嵌套初始化：{{pos.x, pos.y, pos.z}, name}
    return {{0, 0, 0}, name};
}

TH_EXPORT_CPP_API_addNewPlayer(addNewPlayer);
```

> **注意**：在 C++ 侧，仍然按照嵌套 struct 的方式初始化。

## 第三步：编译运行

```sh
taihe-tryit test -u sts cookbook/structext
```

## 使用示例

**File: `user/main.ets`**

```typescript
import * as structext from "structext";

loadLibrary("structext");

function main() {
    let player1 = structext.addNewPlayer("Tom");
    let player2 = structext.addNewPlayer("Jimmy");
    
    console.log("Player1's name is " + player1.name);
    console.log("Player2's name is " + player2.name);
    
    // 直接访问展开的字段
    player2.x += 1;
    player2.y += 1;
    player2.z += 1;
    
    console.log("Player1's position: " + player1.x + "," + player1.y + "," + player1.z);
    console.log("Player2's position: " + player2.x + "," + player2.y + "," + player2.z);
}
```

**输出：**

```
Player1's name is Tom
Player2's name is Jimmy
Player1's position: 0,0,0
Player2's position: 1,1,1
```

---

## `@class` 注解说明

不使用 `@class` 时，struct 会生成为：
- `interface Player` - 用于接收 ArkTS 用户传入
- `class Player_inner implements Player` - 用于 C++ 返回值传出

使用 `@class` 后，直接生成：
- `class Player` - 保证 ArkTS 兼容性

### `@class` 与继承/实现的关系

当使用 `struct Foo { @extends bar: Bar; }` 表示继承关系时，生成的代码取决于 `@class` 注解：

| Foo | Bar | 生成的关系 |
|-----|-----|------------|
| `@class` | `@class` | 类继承类 (`class Foo extends Bar`) |
| `@class` | 无 `@class` | 类实现接口 (`class Foo implements Bar`) |
| 无 `@class` | 无 `@class` | 接口继承接口 (`interface Foo extends Bar`) |
| 无 `@class` | `@class` | ❌ **不支持** |

---

## `@readonly` 只读字段

使用 `@readonly` 注解可以将 struct 字段标记为只读，在 ArkTS 侧生成 `readonly` 修饰符。

**File: `idl/config.taihe`**

```rust
struct Config {
    @readonly name: String;      // readonly name: string
    @readonly version: i32;      // readonly version: int
    description: String;         // description: string (可修改)
}
```

**生成的 ArkTS 代码：**

```typescript
export interface Config {
    readonly name: string;
    readonly version: int;
    description: string;
}
```

**使用示例：**

```typescript
let config: Config = { name: "App", version: 1, description: "My app" };
config.description = "Updated";  // OK
// config.name = "New";          // Error: 只读属性
```

---

## 相关文档

- [继承](../inherit/README.md) - 接口继承
- [Enum 与 Union](../enum_union/README.md) - 枚举和联合类型
