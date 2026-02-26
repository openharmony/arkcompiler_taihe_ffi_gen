# 类继承（Class Extend）

> **注意**：本文档中所介绍的方法已经过时，现在你可以直接使用 [继承](../inherit/README.md#class-注解与继承实现的关系) 教程中介绍的方式来实现类继承，无需使用 `@!sts_inject` 注解。

> **学习目标**：掌握通过 `@!sts_inject` 实现 ArkTS 侧类继承的高级模式。

本教程介绍如何在 ArkTS 侧实现类继承，同时保持与 C++ 数据结构的正确绑定。

## 核心概念

| 概念 | 说明 |
|------|------|
| `*_th` 类型 | C++ 侧的数据结构，仅在实现层使用 |
| `@!sts_inject` | 注入自定义 ArkTS 类，包装 `*_th` 类型 |
| `.inner` 属性 | ArkTS 类访问底层 `*_th` 对象 |

---

## 第一步：定义接口

**File: `idl/hello.taihe`**

```rust
// C++ 侧接口（_th 后缀）
interface UnifiedRecord_th {
    GetType(): void;
}
function CreateUnifiedRecord_noparam_th(): UnifiedRecord_th;

interface Text_th {
    GetDetails(): i32;
    SetDetails(a: i32): void;
}
function CreateText_noparam_th(): Text_th;

interface PlainText_th {
    GetTextContent(): String;
    SetTextContent(a: String): void;
}
function CreatePlainText_noparam_th(): PlainText_th;

// 注入 ArkTS 类定义
@!sts_inject("""
export class UnifiedRecord {
    inner: UnifiedRecord_th;
    getType(): void {
        this.inner.getType();
    }
    constructor() {
        this.inner = createUnifiedRecord_noparam_th();
    }
    constructor(a: UnifiedRecord_th) {
        this.inner = a;
    }
}

export class Text extends UnifiedRecord {
    inner: Text_th;
    getDetails(): int {
        return this.inner.getDetails();
    }
    setDetails(a: int): void {
        this.inner.setDetails(a);
    }
    constructor() {
        this.inner = createText_noparam_th();
    }
    constructor(b: Text_th) {
        this.inner = b;
    }
}

export class PlainText extends Text {
    inner: PlainText_th;
    getTextContent(): String {
        return this.inner.getTextContent();
    }
    setTextContent(a: String): void {
        this.inner.setTextContent(a);
    }
    constructor() {
        this.inner = createPlainText_noparam_th();
    }
    constructor(c: PlainText_th) {
        this.inner = c;
    }
}
""")
```

### 继承关系

```
UnifiedRecord
    ↑
   Text
    ↑
PlainText
```

### 设计规则

| 规则 | 说明 |
|------|------|
| 覆盖父类方法 | 在 `*_th` 接口中声明该方法，ArkTS 调用子类实现 |
| 继承父类方法 | 省略该方法，ArkTS 调用父类实现 |
| 类型转换 | ETS → `_th`：使用 `.inner`；`_th` → ETS：使用构造函数 |

## 第二步：实现 C++ 代码

**File: `author/src/hello.impl.cpp`**

```cpp
#include "hello.impl.hpp"

using namespace taihe;

class UnifiedRecord_thImpl {
public:
    void GetType() {
        std::cout << "GetType in UnifiedRecord" << std::endl;
    }
};

class Text_thImpl {
public:
    int32_t GetDetails() {
        std::cout << "GetDetails in Text" << std::endl;
        return 1;
    }
    void SetDetails(int32_t a) {
        std::cout << "SetDetails in Text" << std::endl;
    }
};

class PlainText_thImpl {
public:
    string GetTextContent() {
        std::cout << "GetTextContent in PlainText" << std::endl;
        return "content";
    }
    void SetTextContent(string_view a) {
        std::cout << "SetTextContent in PlainText" << std::endl;
    }
};

UnifiedRecord_th CreateUnifiedRecord_noparam_th() {
    return make_holder<UnifiedRecord_thImpl, UnifiedRecord_th>();
}

Text_th CreateText_noparam_th() {
    return make_holder<Text_thImpl, Text_th>();
}

PlainText_th CreatePlainText_noparam_th() {
    return make_holder<PlainText_thImpl, PlainText_th>();
}

TH_EXPORT_CPP_API_CreateUnifiedRecord_noparam_th(CreateUnifiedRecord_noparam_th);
TH_EXPORT_CPP_API_CreateText_noparam_th(CreateText_noparam_th);
TH_EXPORT_CPP_API_CreatePlainText_noparam_th(CreatePlainText_noparam_th);
```

## 第三步：编译运行

```sh
taihe-tryit test -u sts cookbook/hello
```

## 使用示例

**File: `user/main.ets`**

```typescript
import { UnifiedRecord, Text, PlainText } from "hello";

loadLibrary("hello");

function main() {
    let record = new UnifiedRecord();
    record.getType();  // GetType in UnifiedRecord
    
    let text = new Text();
    text.getType();     // 继承自 UnifiedRecord
    text.getDetails();  // GetDetails in Text
    
    let plain = new PlainText();
    plain.getType();           // 继承自 UnifiedRecord
    plain.getTextContent();    // GetTextContent in PlainText
}
```

---

## 相关文档

- [继承](../inherit/README.md) - 基本继承
- [类](../class/README.md) - 类、静态方法和构造函数
- [External Object](../external_obj/README.md) - 外部对象处理
