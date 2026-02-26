# 继承

> **学习目标**：掌握 Taihe 中接口继承机制以及 `@class` 注解的使用。

本教程以"银行卡付款系统"为例，介绍接口继承的用法。

## 核心概念

### 继承注解

| 注解 | 作用 | 说明 |
|------|------|------|
| `@class` | 生成类而非接口 | ArkTS 侧投影为 `class` 而非 `interface` |

---

## 第一步：定义接口

**File: `idl/inherit.taihe`**

```rust
interface Payable {
    pay(amountDue: f64): void;
}

@class
interface CreditCard : Payable {
    topUp(topUpAmount: f64): void;
    getBalance(): f64;
}

function makeCreditCard(initAmount: f64): CreditCard;
```

**说明：**
- `CreditCard : Payable` 表示继承自 `Payable` 接口
- `@class` 使 ArkTS 侧生成 `class CreditCard` 而非 `interface CreditCard`

## 第二步：实现 C++ 代码

**File: `author/src/inherit.impl.cpp`**

```cpp
#include "inherit.impl.hpp"

using namespace taihe;

class CreditCardImpl {
public:
    CreditCardImpl(double initAmount) : amount(initAmount) {}

    void topUp(double topUpAmount) {
        amount += topUpAmount;
    }

    double getBalance() {
        return amount;
    }

    // 实现继承自 Payable 的方法
    void pay(double amountDue) {
        if (amountDue > amount) {
            std::cout << "Insufficient balance" << std::endl;
            return;
        }
        amount -= amountDue;
        std::cout << "Payment successful" << std::endl;
    }

private:
    double amount;
};

CreditCard makeCreditCard(double initAmount) {
    return make_holder<CreditCardImpl, CreditCard>(initAmount);
}

TH_EXPORT_CPP_API_makeCreditCard(makeCreditCard);
```

## 第三步：编译运行

```sh
taihe-tryit test -u sts cookbook/inherit
```

## 使用示例

**File: `user/main.ets`**

```typescript
import * as inherit from "inherit";

loadLibrary("inherit");

function main() {
    // 创建银行卡，初始余额 1000
    let card = inherit.makeCreditCard(1000.0);

    // 查看余额
    console.log(card.getBalance());     // 1000

    // 充值
    card.topUp(500.0);
    console.log(card.getBalance());     // 1500

    // 付款（调用继承的方法）
    card.pay(50.0);                     // Payment successful

    // 查看余额
    console.log(card.getBalance());     // 1450
}
```

**输出：**

```
1000
1500
Payment successful
1450
```

---

## C++ 侧调用继承方法

在 C++ 侧，调用继承来的方法需要先转换为父接口类型：

```cpp
CreditCard card = makeCreditCard(100.0);

// ❌ 错误：直接调用继承方法
card->pay(50.0);

// ✅ 正确：转换为父接口的 weak 类型（避免引用计数开销）
weak::Payable(card)->pay(50.0);
```

---

## 继承与实现规则

### interface 与 struct 的继承方式

| 类型 | 继承语法 | 示例 |
|------|----------|------|
| `interface` | 使用 `:` | `interface Derived: Base { }` |
| `struct` | 使用 `@extends` | `struct Derived { @extends base: Base; }` |

> **重要**：只允许 interface 与 interface 之间、struct 与 struct 之间继承，**不允许** interface 和 struct 之间继承/实现。如果 TypeScript 代码中存在这种情况，建议将涉及的类型都改写为 Taihe interface。

### TypeScript 到 Taihe 的转换示例

**带方法的接口继承：**

```typescript
// TypeScript
interface BaseInterface {
    getId(): string;
}

interface DerivedInterface extends BaseInterface {
    getValue(): number;
}
```

转换为：

```rust
// Taihe
interface BaseInterface {
    getId(): String;
}

interface DerivedInterface: BaseInterface {
    getValue(): i32;
}
```

**纯数据接口的继承**（参见 [Struct 继承](../struct_extends/README.md)）：

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

### `@class` 注解与继承/实现的关系

当使用 `interface Foo: Bar` 或 `struct Foo { @extends bar: Bar; }` 表示继承关系时，生成的代码取决于 `@class` 注解：

| Foo | Bar | 生成的关系 |
|-----|-----|------------|
| `@class` | `@class` | 类继承类 (`class Foo extends Bar`) |
| `@class` | 无 `@class` | 类实现接口 (`class Foo implements Bar`) |
| 无 `@class` | 无 `@class` | 接口继承接口 (`interface Foo extends Bar`) |
| 无 `@class` | `@class` | ❌ **不支持** |

---

## 相关文档

- [属性](../property/README.md) - `@get`/`@set` 访问器与 `@readonly` 只读字段
- [Interface 接口](../interface/README.md) - 接口基础定义
- [Struct 继承](../struct_extends/README.md) - 纯数据类型继承
- [多继承](../multiple_inherit/README.md) - 多接口继承
- [多态](../polymorphism/README.md) - 多态特性
