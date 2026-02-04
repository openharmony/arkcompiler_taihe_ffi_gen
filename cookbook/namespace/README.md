# Namespace 命名空间

> **学习目标**：掌握如何在 Taihe 中使用命名空间组织代码。

## 核心概念

Taihe 使用 `@!namespace()` 注解实现 ArkTS 的命名空间。

| 规则 | 说明 |
|------|------|
| 每个文件一个命名空间 | 一个 Taihe 文件只能使用一个 `@!namespace` |
| 推荐文件命名 | `<module_name>.<namespace_name>.taihe` |
| 可以直接创建命名空间 | 无需先创建空的模块文件 |

---

## 语法

```rust
@!namespace("module_name", "namespace_name")
```

---

## 第一步：定义接口

**File: `idl/module1.taihe`**

```rust
function module1Run(): void;
```

**File: `idl/module1.foo.taihe`**

```rust
@!namespace("module1", "foo")

function fooFunc(): void;
```

**File: `idl/module2.bar.taihe`**

```rust
@!namespace("module2", "bar")

function barFunc(): void;
```

> **说明**：`module2.bar.taihe` 可以直接创建，无需先有 `module2.taihe` 文件。

## 第二步：实现 C++ 代码

**File: `author/src/module1.impl.cpp`**

```cpp
#include "module1.impl.hpp"

void module1Run() {
    std::cout << "Module: module1" << std::endl;
}

TH_EXPORT_CPP_API_module1Run(module1Run);
```

**File: `author/src/module1.foo.impl.cpp`**

```cpp
#include "module1.foo.impl.hpp"

namespace module1::foo {

void fooFunc() {
    std::cout << "namespace: module1.foo, func: foo" << std::endl;
}

TH_EXPORT_CPP_API_fooFunc(fooFunc);

}
```

**File: `author/src/module2.bar.impl.cpp`**

```cpp
#include "module2.bar.impl.hpp"

namespace module2::bar {

void barFunc() {
    std::cout << "namespace: module2.bar, func: bar" << std::endl;
}

TH_EXPORT_CPP_API_barFunc(barFunc);

}
```

## 第三步：编译运行

```sh
taihe-tryit test -u sts cookbook/namespace
```

## 使用示例

**File: `user/main.ets`**

```typescript
import * as Module1 from "module1";
import * as Module2 from "module2";

loadLibrary("module1");
loadLibrary("module2");

function main() {
    // 调用模块根函数
    Module1.module1Run();
    
    // 调用命名空间内的函数
    Module1.foo.fooFunc();
    Module2.bar.barFunc();
}
```

**输出：**

```
Module: module1
namespace: module1.foo, func: foo
namespace: module2.bar, func: bar
```

---

## 相关文档

- [Import 导入](../import/README.md) - 模块导入
- [快速参考](../quick_ref/README.md) - 功能速查表
