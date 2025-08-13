# Enum 与 Union

以消息系统为例介绍 taihe 的 `enum` 与 `union`

`enum` 用于使用常量表示有限的状态，`union` 用于在同一内存位置存放不同数据类型

## 第一步：编写接口原型

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

enum 有 2 种语法

1. key -> int
    ```
    enum MessageType: i32 {
        Text = 0,
        Number = 1
    }
    ```
2. key -> string
    ```
    enum MessageType: String {
        Text = "Text",
        Number = "Num"
    }
    ```

## 第二步：完成 C++ 实现

**File: `author/src/message.impl.cpp`**
```cpp
Message createTextMessage(string_view str) {
    return {MessageType::key_t::Text, MessageData::make_textVal(str)};
}

Message createNumberMessage(int64_t num) {
    return {MessageType::key_t::Number, MessageData::make_numVal(num)};
}

void processMessage(Message const& msg) {
    switch(msg.type.get_key()) {
        case MessageType::key_t::Text:
            std::cout << "text: " << msg.data.get_textVal_ref() << std::endl;
            break;
        case MessageType::key_t::Number:
            std::cout << "num: " << msg.data.get_numVal_ref() << std::endl;
            break;
    }
}
```

此实现有 4 个要点：1 如何创建 enum；2 如何获取 enum 信息；3 如何创建 union；4 如何读取 union 的值

1. `key_t`

    以本例 enum 为例，用户可以使用 `MessageType::key_t::Text` 与 `MessageType::key_t::Number` 来构造 enum，即：使用 `{enum}::key_t::{key}` 来构造 enum

2. `get_key()` 与 `get_value()`

    使用 `get_key()` 与 `get_value()` 可以获取 enum 的键与值

3. make

    以本例 union 为例，用户可以使用 `MessageData::make_textVal(str)` 与 `MessageData::make_numVal(num)` 来构造 union，即：使用 `{union}::make_{union_item}({val})` 来构造 union

4. `get_xxx_ref()`

    以本例 union 为例，用户可以使用 `get_textVal_ref()` 与 `get_numVal_ref()` 来获取 union 的值，即：使用 `get_{union_item}_ref` 来获取 union 的值

## 第三步：在 ets 侧使用

```typescript
// 创建文本信息
let textMsg = message.createTextMessage("hello");
// 创建数字信息
let numMsg = message.createNumberMessage(12345);
// 输出信息
message.processMessage(textMsg);
message.processMessage(numMsg);
```

Output:
```sh
text: hello
num: 12345
```

## `const` 常量

如果用户希望在 Taihe 里定义 `const` 常量

可以在 enum 上使用 `@const`
```rust
@const
enum Flags: i32 {
    FLAG_I32_A = 1,
    FLAG_I32_B = 2,
}
```

在 ets 文件中，可以直接使用 `{pkg_name}.FLAG_I32_A` 或 `{pkg_name}.FLAG_I32_B`
```typescript
import * as ConstPkg from "xxx";

const val = ConstPkg.FLAG_I32_A;
```