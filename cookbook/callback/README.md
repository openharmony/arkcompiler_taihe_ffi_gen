# Callback 回调

> **学习目标**：掌握如何将函数作为参数传递，实现回调机制。

回调（Callback）是指将一个函数作为参数传给另一个函数，在合适的时机调用它。这是实现异步操作、事件处理等功能的常用模式。

## 语法说明

在 Taihe IDL 中，回调函数的语法为：

```rust
(参数名: 类型, ...) => 返回类型
```

## 第一步：定义回调函数

**File: `idl/callback.taihe`**

```rust
// 无参数无返回值
function cb_void_void(f: () => void): void;

// 有参数无返回值
function cb_i_void(f: (a: i32) => void): void;

// 有参数有返回值
function cb_str_str(f: (a: String) => String): String;

// 使用 struct 作为参数和返回值
struct Person {
    name: String;
    age: i32;
}

function cb_struct(f: (data: Person) => Person): void;
```

## 第二步：实现 C++ 代码

在 C++ 中，回调类型映射为 `callback_view<返回类型(参数类型...)>`：

**File: `author/src/callback.impl.cpp`**

```cpp
#include "callback.impl.hpp"

using namespace taihe;

void cb_void_void(callback_view<void()> f) {
    f();  // 直接调用回调
}

void cb_i_void(callback_view<void(int32_t)> f) {
    f(1);  // 传递参数调用回调
}

string cb_str_str(callback_view<string(string_view)> f) {
    string out = f("hello");  // 调用并获取返回值
    return out;
}

void cb_struct(callback_view<::callback::Person(::callback::Person const&)> f) {
    ::callback::Person input{"Tom", 18};
    ::callback::Person result = f(input);
    std::cout << result.name << " " << result.age << std::endl;
}

TH_EXPORT_CPP_API_cb_void_void(cb_void_void);
TH_EXPORT_CPP_API_cb_i_void(cb_i_void);
TH_EXPORT_CPP_API_cb_str_str(cb_str_str);
TH_EXPORT_CPP_API_cb_struct(cb_struct);
```

> **💡 类型映射**
>
> | IDL 回调类型 | C++ 类型 |
> |-------------|----------|
> | `() => void` | `callback_view<void()>` |
> | `(a: i32) => String` | `callback_view<string(int32_t)>` |
> | `(a: T) => R` | `callback_view<R(T)>` |

## 第三步：在 ArkTS 中使用

**File: `user/main.ets`**

```typescript
import * as cb from "callback";

loadLibrary("callback");

function main() {
    // 无参数无返回值
    cb.cb_void_void(() => {
        console.log("void callback called!");
    });

    // 有参数无返回值
    cb.cb_i_void((a: int) => {
        console.log("received: " + a);
    });

    // 有参数有返回值
    let result = cb.cb_str_str((a: string) => {
        console.log("input: " + a);
        return "processed: " + a;
    });
    console.log("result: " + result);

    // 使用 struct
    cb.cb_struct((person: cb.Person) => {
        return new cb.Person(person.name + " Jr.", person.age + 10);
    });
}
```

**输出：**

```
void callback called!
received: 1
input: hello
result: processed: hello
Tom Jr. 28
```

---

## 相关文档

- [Callback 比较](../callback_compare/README.md) - 判断回调对象是否相等
- [异步 async/promise](../async/README.md) - 异步编程模式
- [On/Off 事件](../on_off/README.md) - 事件订阅机制
