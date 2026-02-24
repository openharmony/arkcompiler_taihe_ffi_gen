# 重写（Override）

> **学习目标**：掌握如何在 ArkTS 侧继承 Taihe 接口并重写方法。

## 核心概念

Taihe 支持在 ArkTS 侧创建子类，继承 Taihe 定义的父类，并重写其方法。

### 相关注解

| 注解 | 作用 | 示例 |
|------|------|------|
| `@class` | 生成 class 而非 interface | `@class interface UIAbility` |
| `@ctor("Class")` | 添加构造器 | `@ctor("UIAbility") function create()` |
| `@static("Class")` | 添加静态方法 | `@static("UIAbility") function log()` |
| `@rename` | 重命名 | `@rename("logLifecycle") @static("OtherAbility") function logLifecycleInOtherAbility()` |

---

## 第一步：定义接口

**File: `idl/override.taihe`**

```rust
@class
interface UIAbility {
    onForeground(): void;
    onBackground(): void;
}

// 匿名构造函数（单构造函数时推荐）
@ctor("UIAbility")
function getUIAbility(): UIAbility;

function useUIAbility(a: UIAbility): void;

// 静态方法
@static("UIAbility")
function logLifecycle(str: String): void;

@class
interface OtherAbility {}

// @static 可以和 @rename 结合使用，logLifecycleInOtherAbility 会被生成为 OtherAbility.logLifecycle
@static("OtherAbility")
@rename("logLifecycle")
function logLifecycleInOtherAbility(str: String): void;
```

### 构造函数使用规则

**单构造函数**（使用 `@ctor` 直接匿名化）：

```rust
@class
interface IfaceA {}

@ctor("IfaceA")
function createIfaceA(): IfaceA;
```

**多构造函数**（命名构造函数）：

```rust
@class
interface IfaceB {}

@ctor("IfaceB")
function createIfaceBWithInt(arg: i32): IfaceB;

@ctor("IfaceB")
function createIfaceBWithString(arg: String): IfaceB;
```

## 第二步：实现 C++ 代码

**File: `author/src/override.impl.cpp`**

```cpp
#include "override.impl.hpp"

using namespace taihe;
using namespace override;

class UIAbilityImpl {
public:
    void onForeground() {
        std::cout << "in cpp onForeground" << std::endl;
    }
    void onBackground() {
        std::cout << "in cpp onBackground" << std::endl;
    }
};

UIAbility getUIAbility() {
    return make_holder<UIAbilityImpl, UIAbility>();
}

void useUIAbility(weak::UIAbility a) {
    a->onForeground();  // 可能调用重写的方法
    a->onBackground();  // 可能调用重写的方法
}

void logLifecycle(string_view str) {
    std::cout << "[UIAbility]: " << str << std::endl;
}

TH_EXPORT_CPP_API_getUIAbility(getUIAbility);
TH_EXPORT_CPP_API_useUIAbility(useUIAbility);
TH_EXPORT_CPP_API_logLifecycle(logLifecycle);
```

## 第三步：编译运行

```sh
taihe-tryit test -u sts cookbook/override -Carkts:keep-name
```

## 使用示例

**File: `user/main.ets`**

```typescript
import { UIAbility, useUIAbility } from "override";

loadLibrary("override");

// 继承并重写方法
class MyAbility extends UIAbility {
    constructor() {
        super();
    }
    
    // 重写 onForeground
    onForeground(): void {
        console.log("in ets onForeground");
    }
    // onBackground 继承自父类，不重写
}

function main() {
    let my_ability: UIAbility = new MyAbility();
    
    // C++ 会调用重写的 onForeground 和原始的 onBackground
    useUIAbility(my_ability);
    
    // 调用静态方法
    MyAbility.logLifecycle("using uiability");
}
```

**输出：**

```
in ets onForeground
in cpp onBackground
[UIAbility]: using uiability
```

> **说明**：`useUIAbility` 在 C++ 中调用时，`onForeground()` 实际执行的是 ArkTS 侧重写的版本，`onBackground()` 执行的是 C++ 原始版本。

---

## 相关文档

- [继承](../inherit/README.md) - 接口继承基础
- [多态](../polymorphism/README.md) - 多态特性
