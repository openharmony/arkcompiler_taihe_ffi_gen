# Enum 与 Union

> **学习目标**：掌握 Taihe 中枚举（Enum）和联合类型（Union）的定义与使用。

本教程以"消息系统"为例，介绍 `enum` 与 `union` 的用法。

## 核心概念

| 类型 | 用途 | 类比 |
|------|------|------|
| `enum` | 表示有限的常量集合 | C++ enum class |
| `union` | 同一位置存放不同数据类型 | C++ std::variant |

---

## Enum 语法

Taihe 支持两种 enum 映射：

```rust
// 方式一：key -> int
enum MessageType: i32 {
    Text = 1;
    Number = 2;
}

// 方式二：key -> string
enum Status: String {
    Success = "success";
    Failed = "failed";
}
```

## Union 语法

```rust
interface Base {}

interface Derived: Base {}

union MessageData {
    @undefined uValue: unit;                // undefined
    nValue: unit;                           // null
    derivedValue: Derived;                  // 子类型
    baseValue: Base;                        // 基类型
    stringValue: String;                    // 基础类型
    recordValue: @record Map<String, i32>;  // 容器类型
    opaqueValue: Opaque;                    // Object
}
```

> **注意**：由于 Taihe union 在从 ArkTS 传入 C++ 侧时，会按照声明顺序依次匹配成员类型，因此在声明 union 时应遵循以下规则：
> 1. 不能同时包含多个相同类型的成员。
> 2. 不能同时有多个同一种类的类型擦除容器类型的成员（例如 `@record Map<String, i32>` 和 `@record Map<String, String>` 在 ArkTS 中都会被擦除为 `Record<any, any>`）。
> 3. 如果有 `undefined` 或者 `null` 成员，必须放在其它成员之前，且 `undefined` 成员须在 `null` 成员之前。
> 4. 如果同时包含基类型和子类型，基类型成员必须放在子类型成员之后。
> 5. 如果存在 `Object` 成员，必须放在其它所有成员之后。

---

## 第一步：定义接口

**File: `idl/message.taihe`**

```rust
enum MessageType: i32 {
    Text = 1;
    Number = 2;
}

union MessageData {
    textVal: String;
    numVal: i64;
}

struct Message {
    type: MessageType;
    data: MessageData;
}

function createTextMessage(str: String): Message;
function createNumberMessage(num: i64): Message;
function processMessage(msg: Message): void;
```

## 第二步：实现 C++ 代码

**File: `author/src/message.impl.cpp`**

```cpp
#include "message.impl.hpp"

using namespace taihe;

Message createTextMessage(string_view str) {
    return {MessageType::key_t::Text, MessageData::make_textVal(str)};
}

Message createNumberMessage(int64_t num) {
    return {MessageType::key_t::Number, MessageData::make_numVal(num)};
}

void processMessage(Message const& msg) {
    switch (msg.type.get_key()) {
        case MessageType::key_t::Text:
            std::cout << "text: " << msg.data.get_textVal_ref() << std::endl;
            break;
        case MessageType::key_t::Number:
            std::cout << "num: " << msg.data.get_numVal_ref() << std::endl;
            break;
    }
}

TH_EXPORT_CPP_API_createTextMessage(createTextMessage);
TH_EXPORT_CPP_API_createNumberMessage(createNumberMessage);
TH_EXPORT_CPP_API_processMessage(processMessage);
```

### C++ API 参考

#### Enum 操作

| 操作 | 语法 | 示例 |
|------|------|------|
| 创建 enum | `{Enum}::key_t::{Key}` | `MessageType::key_t::Text` |
| 获取 key | `.get_key()` | `msg.type.get_key()` |
| 获取 value | `.get_value()` | `msg.type.get_value()` |

#### Union 操作

| 操作 | 语法 | 示例 |
|------|------|------|
| 创建 union | `{Union}::make_{item}(value)` | `MessageData::make_textVal(str)` |
| 获取值（引用） | `.get_{item}_ref()` | `msg.data.get_textVal_ref()` |
| 获取当前类型 | `.get_key()` | `msg.data.get_key()` |

## 第三步：编译运行

```sh
taihe-tryit test -u sts cookbook/message
```

## 使用示例

**File: `user/main.ets`**

```typescript
import * as message from "message";

loadLibrary("message");

function main() {
    // 创建文本消息
    let textMsg = message.createTextMessage("hello");
    // 创建数字消息
    let numMsg = message.createNumberMessage(12345);
    
    // 处理消息
    message.processMessage(textMsg);
    message.processMessage(numMsg);
}
```

**输出：**

```
text: hello
num: 12345
```

---

## 进阶：`@const` 常量

使用 `@const` 注解可以将 enum 导出为全局常量：

```rust
@const
enum Flags: i32 {
    FLAG_A = 1;
    FLAG_B = 2;
}
```

在 ArkTS 中直接使用：

```typescript
import * as pkg from "flags";

const val = pkg.FLAG_A;  // 直接访问常量
```

---

## 相关文档

- [Struct 结构体](../struct_extends/README.md) - 结构体定义
- [Optional 可选类型](../optional/README.md) - 可选值处理
- [多态](../polymorphism/README.md) - 利用 union 实现跨语言多态
