# 属性（Property）

> **学习目标**：掌握 Taihe 中属性相关注解 `@get`、`@set` 和 `@readonly` 的使用。

本教程介绍如何使用属性注解来声明 getter/setter 访问器和只读字段。

## 核心概念

| 注解 | 适用于 | 作用 |
|------|--------|------|
| `@get` | interface 方法 | 将方法映射为 ArkTS getter 属性 |
| `@set` | interface 方法 | 将方法映射为 ArkTS setter 属性 |
| `@readonly` | struct 字段 | 在 ArkTS 侧生成 `readonly` 修饰符 |

### `@get` / `@set` 命名规则

- **带参数**：`@get("balance")` 直接指定属性名
- **无参数**：方法名必须以 `get`/`set` 开头，属性名取剩余部分并首字母小写
  - `getCount()` → 属性名 `count`
  - `setLabel()` → 属性名 `label`

---

## 第一步：定义接口

**File: `idl/property.taihe`**

```rust
// @readonly：struct 的只读字段
struct Config {
    @readonly name: String;
    @readonly version: i32;
    description: String;
}

// @get / @set：interface 的属性访问器
@class
interface Counter {
    @get getCount(): i32;
    @get("label") getLabel(): String;
    @set setLabel(val: String): void;
    increment(): void;
}

function createConfig(name: String, version: i32, description: String): Config;
function createCounter(label: String): Counter;
```

**说明：**
- `Config.name` 和 `Config.version` 使用 `@readonly`，在 ArkTS 侧不可修改
- `Counter.count` 只有 `@get`，为只读属性
- `Counter.label` 同时有 `@get` 和 `@set`，为可读写属性

### 生成的 ArkTS 代码

`@readonly` 生成：

```typescript
export interface Config {
    readonly name: string;
    readonly version: int;
    description: string;
}
```

`@get` / `@set` 生成：

```typescript
export class Counter {
    get count(): int { ... }
    get label(): string { ... }
    set label(val: string) { ... }
    increment(): void { ... }
}
```

## 第二步：实现 C++ 代码

**File: `author/src/property.impl.cpp`**

```cpp
#include "property.impl.hpp"

using namespace taihe;

class CounterImpl {
public:
    CounterImpl(string_view label) : count_(0), label_(label) {}

    int32_t getCount() { return count_; }

    string getLabel() { return label_; }

    void setLabel(string_view val) {
        label_ = std::string(val.data(), val.size());
    }

    void increment() {
        ++count_;
        std::cout << label_ << ": " << count_ << std::endl;
    }

private:
    int32_t count_;
    std::string label_;
};

Config createConfig(string_view name, int32_t version, string_view description) {
    return {name, version, description};
}

Counter createCounter(string_view label) {
    return make_holder<CounterImpl, Counter>(label);
}

TH_EXPORT_CPP_API_createConfig(createConfig);
TH_EXPORT_CPP_API_createCounter(createCounter);
```

## 第三步：编译运行

```sh
taihe-tryit test -u ani cookbook/property
```

## 使用示例

**File: `user/main.ets`**

```typescript
import * as property from "property";

loadLibrary("property");

function main() {
    // @readonly 示例
    let config = property.createConfig("MyApp", 1, "A demo app");
    console.log(config.name);           // MyApp
    console.log(config.version);        // 1
    // config.name = "New";             // Error: readonly 属性不可修改
    config.description = "Updated";     // OK

    // @get / @set 示例
    let counter = property.createCounter("step");
    console.log(counter.count);         // 0
    console.log(counter.label);         // step
    counter.label = "tick";             // 通过 setter 修改
    counter.increment();                // tick: 1
    counter.increment();                // tick: 2
    console.log(counter.count);         // 2
}
```

**输出：**

```
MyApp
1
A demo app
Updated
0
step
tick
tick: 1
tick: 2
2
```

---

## 相关文档

- [继承](../inherit/README.md) - 接口继承与 `@class` 注解
- [Struct 继承](../struct_extends/README.md) - 纯数据类型继承与 `@extends`
- [Interface 接口](../interface/README.md) - 接口基础定义
