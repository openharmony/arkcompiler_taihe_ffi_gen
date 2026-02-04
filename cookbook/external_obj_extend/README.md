# External Object Extend（继承外部类）

> **学习目标**：掌握如何继承外部 ArkTS 类并在 C++ 中实现方法覆盖。

## 核心概念

通过 `@!sts_inject` 注解将 ArkTS 类定义注入，使 Taihe 生成的类能够继承外部类。

| 组件 | 作用 |
|------|------|
| 外部类 | 已存在的 ArkTS 类（如 `Context`） |
| `*_inner` 接口 | C++ 侧的内部实现 |
| 注入的 ArkTS 类 | 继承外部类，委托到 `*_inner` |

---

## 第一步：定义接口

假设需要继承外部类 `Context`，并覆盖其 `stop()` 方法。

**外部类定义：**

```typescript
// other.subsystem
export class Context {
    start(): string { return "Context start"; }
    stop(): string { return "Context stop"; }
}
```

**File: `idl/external_obj_extend.taihe`**

```rust
// 导入外部类
@!sts_inject("import {Context} from 'other.subsystem';")

// C++ 内部接口（只声明需要覆盖的方法）
@class
interface MyContext_inner {
    stop(): String;
}

function createMyContext_inner(): MyContext_inner;

// 注入继承外部类的 ArkTS 类
@!sts_inject("
export class MyContext extends Context {
    inner: MyContext_inner;
    
    // 覆盖 stop 方法
    stop(): string {
        return this.inner.stop();
    }
    
    constructor() {
        this.inner = createMyContext_inner();
    }
    constructor(arg: MyContext_inner) {
        this.inner = arg;
    }
}
")
```

### 设计思路

1. `MyContext_inner` 只声明需要覆盖的方法
2. `MyContext` 继承 `Context`，未覆盖的方法自动使用父类实现
3. 覆盖的方法委托给 `inner` 对象

## 第二步：实现 C++ 代码

**File: `author/src/external_obj_extend.impl.cpp`**

```cpp
#include "external_obj_extend.impl.hpp"

using namespace taihe;
using namespace external_obj_extend;

class MyContext_innerImpl {
public:
    // 实现覆盖的方法
    string stop() {
        return "MyContext stop";  // 自定义实现
    }
};

MyContext_inner createMyContext_inner() {
    return make_holder<MyContext_innerImpl, MyContext_inner>();
}

TH_EXPORT_CPP_API_createMyContext_inner(createMyContext_inner);
```

## 第三步：编译运行

```sh
taihe-tryit test -u sts cookbook/external_obj_extend
```

## 使用示例

**File: `user/main.ets`**

```typescript
import { Context } from "other.subsystem";
import * as lib from "external_obj_extend";

loadLibrary("external_obj_extend");

function main() {
    let context = new Context();
    console.log("base: ", context.start(), context.stop());
    // base: Context start Context stop
    
    let mycontext = new lib.MyContext();
    console.log("sub: ", mycontext.start(), mycontext.stop());
    // sub: Context start MyContext stop  （start 使用父类，stop 使用覆盖）
}
```

**输出：**

```
base: Context start Context stop
sub: Context start MyContext stop
```

---

## 相关文档

- [类继承](../class_extend/README.md) - Taihe 内部类继承
- [External Object](../external_obj/README.md) - 外部对象处理
