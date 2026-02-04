# Null 与 Undefined

> **学习目标**：掌握如何在 Taihe 中表示 null 和 undefined 类型。

## 核心概念

Taihe 使用 `union` 配合注解来表示 null 和 undefined 类型。

| Taihe 表示 | ArkTS 类型 |
|------------|------------|
| `nValue: unit` | `null` |
| `@undefined uValue: unit` | `undefined` |

> **注意**：默认情况下，`unit` 类型映射为 `null`；使用 `@undefined` 注解后映射为 `undefined`。

---

## 第一步：定义接口

**File: `idl/nullabletype.taihe`**

```rust
union NullableValue {
    sValue: String;              // 字符串值
    iValue: i32;                 // 整数值
    @undefined uValue: unit;     // undefined
    nValue: unit;                // null
}

function makeNullableValue(tag: i32): NullableValue;
```

## 第二步：实现 C++ 代码

**File: `author/src/nullabletype.impl.cpp`**

```cpp
#include "nullabletype.impl.hpp"

using namespace taihe;
using namespace nullabletype;

constexpr int32_t TAG_NULL = 0;
constexpr int32_t TAG_STRING = 1;
constexpr int32_t TAG_INT = 2;

NullableValue makeNullableValue(int32_t tag) {
    switch (tag) {
        case TAG_NULL:
            return NullableValue::make_nValue();     // null
        case TAG_STRING:
            return NullableValue::make_sValue("hello");
        case TAG_INT:
            return NullableValue::make_iValue(123);
        default:
            return NullableValue::make_uValue();     // undefined
    }
}

TH_EXPORT_CPP_API_makeNullableValue(makeNullableValue);
```

### C++ 创建方法

| 创建 | 方法 |
|------|------|
| null | `Union::make_nValue()` |
| undefined | `Union::make_uValue()` |
| 有值 | `Union::make_sValue("hello")` |

## 第三步：编译运行

```sh
taihe-tryit test -u sts cookbook/nullabletype
```

## 使用示例

**File: `user/main.ets`**

```typescript
import { makeNullableValue } from "nullabletype";

loadLibrary("nullabletype");

function main() {
    let nvalue = makeNullableValue(0);   // null
    console.log("null: " + nvalue);
    
    let svalue = makeNullableValue(1);   // "hello"
    console.log("string: " + svalue);
    
    let ivalue = makeNullableValue(2);   // 123
    console.log("int: " + ivalue);
    
    let uvalue = makeNullableValue(10);  // undefined
    console.log("undefined: " + uvalue);
}
```

**输出：**

```
null: null
string: hello
int: 123
undefined: undefined
```

---

## 相关文档

- [Enum 与 Union](../enum_union/README.md) - Union 详细用法
- [Optional](../optional/README.md) - 可选类型
- [Taihe C++](../taihe_cpp/README.md) - C++ API 参考
