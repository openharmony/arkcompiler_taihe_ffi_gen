# 反向调用（Reversed Call）

> **学习目标**：掌握如何在 C++ 中调用 ArkTS 侧已有的接口实现。

## 使用场景

用户在 ArkTS 侧已有接口定义和实现，希望在 C++ 代码中调用这些实现。

---

## 第一步：定义接口

**用户已有的 ArkTS 接口和实现：**

```typescript
// user_impl.ets
export interface IfaceA {
    foo(): string;
    bar(): int;
}

export class ClassA implements IfaceA {
    name: string = "";
    age: int;

    constructor(name: string, age: int) {
        this.name = name;
        this.age = age;
    }

    foo(): string { return this.name; }
    bar(): int { return this.age; }
}
```

**File: `idl/impl.taihe`**

```rust
// 定义对应的 Taihe 接口（使用不同名称）
interface IfaceA_taihe {
    Foo(): String;
    Bar(): i32;
}
```

**File: `idl/native_user.taihe`**

```rust
use impl;

function UseIfaceA(obj: impl.IfaceA_taihe): String;
```

## 第二步：实现 C++ 代码

**File: `author/src/native_user.impl.cpp`**

```cpp
#include "native_user.impl.hpp"
#include "impl.proj.hpp"

using namespace taihe;

string UseIfaceA(impl::weak::IfaceA_taihe obj) {
    // 在 C++ 侧调用 ArkTS 实现的方法
    std::cout << "native call Foo(): " << obj->Foo() << std::endl;
    std::cout << "native call Bar(): " << obj->Bar() << std::endl;
    return obj->Foo();
}

TH_EXPORT_CPP_API_UseIfaceA(UseIfaceA);
```

> **说明**：`impl.taihe` 不需要 C++ 实现，它只是类型声明。

## 第三步：修改 ArkTS 实现

让已有的类同时实现 Taihe 接口：

**File: `user/user_impl.ets`**

```typescript
import * as impl_taihe from "impl";

// 添加 impl_taihe.IfaceA_taihe 到 implements 列表
export class ClassA implements IfaceA, impl_taihe.IfaceA_taihe {
    name: string = "";
    age: int;

    constructor(name: string, age: int) {
        this.name = name;
        this.age = age;
    }

    foo(): string { return this.name; }
    bar(): int { return this.age; }
}
```

## 第四步：编译运行

```sh
taihe-tryit test -u sts cookbook/native_user
```

## 使用示例

**File: `user/main.ets`**

```typescript
import * as user_impl from "user_impl";
import * as native_user from "native_user";

loadLibrary("native_user");

function main() {
    let obj = new user_impl.ClassA("Tom", 18);
    let result = native_user.useIfaceA(obj);
    console.log("ETS return: " + result);
}
```

**输出：**

```
native call Foo(): Tom
native call Bar(): 18
ETS return: Tom
```

---

## C++ 调用接口方法

```cpp
// 使用 -> 调用接口方法
obj->Foo();
obj->Bar();

// weak 类型转换
weak::Base weakObj = obj;
Base strongObj = Base(weakObj);
```

---

## 相关文档

- [Interface 接口](../interface/README.md) - 接口定义
- [Callback](../callback/README.md) - 回调函数
