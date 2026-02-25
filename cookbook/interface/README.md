# Interface 接口

> **学习目标**：掌握如何定义和实现 Taihe 接口，理解接口的创建与使用方式。

在 [绑定机制](../binding/README.md) 中我们学习了 `struct` 的使用。本教程介绍 Taihe 的 `interface` 类型——用于定义带有方法的对象接口。

## 核心概念

- **Interface**：定义一组方法签名，类似于面向对象语言中的接口
- **工厂函数**：由于 interface 需要实现，必须提供一个全局函数来创建实例
- **make_holder**：Taihe 提供的函数，用于将 C++ 实现类绑定到接口

## 第一步：定义接口

在 IDL 文件中定义接口和创建函数：

**File: `idl/interface.taihe`**

```rust
interface ICalculator {
    add(a: i32, b: i32): i32;
    sub(a: i32, b: i32): i32;
    getLastResult(): i32;
    reset(): void;
}

// 工厂函数，用于创建接口实例
function makeCalculator(): ICalculator;

// 接口可以作为函数参数
function restartCalculator(a: ICalculator): void;
```

## 第二步：实现接口

编写 C++ 类实现接口方法，并使用 `make_holder` 绑定：

**File: `author/src/interface.impl.cpp`**

```cpp
#include "interface.impl.hpp"

using namespace taihe;

class MyCalculator {
public:
    // 构造函数参数可以自由定义
    MyCalculator(int32_t init) : lastResult(init) {}

    int32_t add(int32_t a, int32_t b) {
        lastResult = a + b;
        return lastResult;
    }

    int32_t sub(int32_t a, int32_t b) {
        lastResult = a - b;
        return lastResult;
    }

    int32_t getLastResult() {
        return lastResult;
    }

    void reset() {
        lastResult = 0;
    }

private:
    int32_t lastResult = 0;
};

// 工厂函数实现
::interface::ICalculator makeCalculator() {
    // make_holder<实现类, 接口类型>(构造函数参数...)
    return make_holder<MyCalculator, ::interface::ICalculator>(0);
}

// 接口作为参数时使用 weak:: 命名空间
void restartCalculator(::interface::weak::ICalculator a) {
    a->reset();  // 使用 -> 调用方法
}

TH_EXPORT_CPP_API_makeCalculator(makeCalculator);
TH_EXPORT_CPP_API_restartCalculator(restartCalculator);
```

> **⚠️ 注意事项**
>
> - 使用 `make_holder<Impl, Interface>()` 创建接口实例
> - 接口参数类型使用 `weak::` 命名空间
> - 调用接口方法使用 `->` 而非 `.`

## 第三步：编译运行

```sh
taihe-tryit test -u sts cookbook/interface
```

## 使用示例

**File: `user/main.ets`**

```typescript
import * as calc from "interface";

loadLibrary("interface");

function main() {
    let cal = calc.makeCalculator();

    // 调用接口方法
    let result1 = cal.add(1, 2);
    console.log("1 + 2 = " + result1);

    let result2 = cal.sub(1, 2);
    console.log("1 - 2 = " + result2);

    console.log("Last result: " + cal.getLastResult());

    // 将接口作为参数传递
    calc.restartCalculator(cal);
    console.log("After reset: " + cal.getLastResult());
}
```

**输出：**

```
1 + 2 = 3
1 - 2 = -1
Last result: -1
After reset: 0
```

---

## 相关文档

- [继承](../inherit/README.md) - 接口继承与属性
- [多继承](../multiple_inherit/README.md) - 实现多个接口
- [类](../class/README.md) - 类、静态方法和构造函数
