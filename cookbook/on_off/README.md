# On/Off 事件监听

> **学习目标**：掌握如何使用 `@on_off` 注解实现 ArkTS 的 on/off 事件监听模式。

## 核心概念

ArkTS 中常见的事件监听接口形式：

```typescript
on(type: "event", callback: () => void): void;
off(type: "event", callback: () => void): void;
```

Taihe 提供 `@on_off` 注解，自动将函数转换为这种形式。

### 注解语法

| 语法 | 说明 |
|------|------|
| `@on_off` | 自动从函数名提取 type 和 funcName |
| `@on_off("typeName")` | 指定 type 名称 |
| `@on_off(name = "funcName")` | 指定生成的函数名 |
| `@on_off("typeName", name = "funcName")` | 同时指定 |

### 自动推导规则

当省略参数时：
- **funcName**：函数名必须以 `on` 或 `off` 开头，使用 `on` 或 `off` 作为生成的函数名
- **typeName**：使用函数名去掉 `on`/`off` 前缀后的部分（首字母转小写）

**示例**：`onFooBar(cb: () => void)` → `on(type: "fooBar", cb: () => void)`

---

## 第一步：定义接口

**File: `idl/on_off.taihe`**

```rust
// 全局函数 - 自动推导
@on_off
function onFoo(a: () => void): void;  // -> on(type: "foo", ...)

@on_off
function offFoo(a: () => void): void; // -> off(type: "foo", ...)

// 全局函数 - 指定 type
@on_off("myEvent")
function onBar(a: i32, cb: () => void): void;  // -> on(type: "myEvent", ...)

@on_off("myEvent")
function offBar(a: i32, cb: () => void): void; // -> off(type: "myEvent", ...)

// 接口方法
interface IObserver {
    @on_off
    onSet(a: () => void): void;   // -> on(type: "set", ...)

    @on_off
    offSet(a: () => void): void;  // -> off(type: "set", ...)

    @on_off("customType")
    onTest(): i32;                // -> on(type: "customType"): int
}

function getObserver(): IObserver;
```

### 与 `@static` 配合使用

```rust
@class
interface EventEmitter {
    emit(event: String): void;
}

@static("EventEmitter")
@on_off
function onEvent(cb: () => void): void;  // -> EventEmitter.on(type: "event", ...)

@static("EventEmitter")
@on_off
function offEvent(cb: () => void): void; // -> EventEmitter.off(type: "event", ...)
```

## 第二步：实现 C++ 代码

**File: `author/src/on_off.impl.cpp`**

```cpp
#include "on_off.impl.hpp"

using namespace taihe;

// 全局函数实现
void onFoo(callback_view<void()> a) {
    std::cout << "onFoo called" << std::endl;
    a();  // 调用回调
}

void offFoo(callback_view<void()> a) {
    std::cout << "offFoo called" << std::endl;
    a();
}

void onBar(int32_t a, callback_view<void()> cb) {
    std::cout << "onBar: " << a << std::endl;
    cb();
}

void offBar(int32_t a, callback_view<void()> cb) {
    std::cout << "offBar: " << a << std::endl;
    cb();
}

// 接口实现类
class ObserverImpl {
public:
    void onSet(callback_view<void()> a) {
        std::cout << "IObserver::onSet" << std::endl;
        a();
    }
    
    void offSet(callback_view<void()> a) {
        std::cout << "IObserver::offSet" << std::endl;
        a();
    }
    
    int32_t onTest() {
        std::cout << "IObserver::onTest" << std::endl;
        return 42;
    }
};

IObserver getObserver() {
    return make_holder<ObserverImpl, IObserver>();
}

TH_EXPORT_CPP_API_onFoo(onFoo);
TH_EXPORT_CPP_API_offFoo(offFoo);
TH_EXPORT_CPP_API_onBar(onBar);
TH_EXPORT_CPP_API_offBar(offBar);
TH_EXPORT_CPP_API_getObserver(getObserver);
```

## 第三步：编译运行

```sh
taihe-tryit test -u sts cookbook/on_off
```

## 使用示例

**File: `user/main.ets`**

```typescript
import * as onoff from "on_off";

loadLibrary("on_off");

function main() {
    // 全局函数调用
    onoff.on("foo", () => { console.log("foo callback"); });
    onoff.off("foo", () => { console.log("foo off callback"); });
    
    onoff.on("myEvent", 123, () => { console.log("myEvent callback"); });
    onoff.off("myEvent", 123, () => { console.log("myEvent off callback"); });
    
    // 接口方法调用
    let observer = onoff.getObserver();
    observer.on("set", () => { console.log("set callback"); });
    observer.off("set", () => { console.log("set off callback"); });
    
    let result = observer.on("customType");
    console.log("customType result: " + result);
}
```

**输出：**

```
foo callback
onFoo called
foo off callback
offFoo called
myEvent callback
onBar: 123
myEvent off callback
offBar: 123
set callback
IObserver::onSet
set off callback
IObserver::offSet
IObserver::onTest
customType result: 42
```

---

## 高级用法

### 自定义函数名

使用 `name` 参数指定生成的函数名（而非 `on`/`off`）：

```rust
@on_off(name = "subscribe")
function subscribeEvent(cb: () => void): void;
// 生成: subscribe(type: "event", cb: () => void): void
```

### 同参数不同回调类型

```rust
@on_off("funcI")
function onFuncI(a: (b: i32) => void): void;

@on_off("funcB")
function onFuncB(a: (b: bool) => void): void;
```

---

## 相关文档

- [Callback 回调](../callback/README.md) - 回调函数的基础用法
- [重命名](../rename_example/README.md) - `@rename` 注解
- [静态方法](../override/README.md) - `@static` 注解

