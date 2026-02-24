# 异步函数

> **学习目标**：掌握 Taihe 中异步函数（`@async` 和 `@promise`）的声明与使用。

## 核心概念

Taihe 支持将 C++ 同步代码自动包装为 ArkTS 异步函数。

| 注解 | 生成的 ArkTS 函数类型 | 使用方式 |
|------|----------------------|----------|
| `@async` | 回调式异步函数 | `func(args, callback)` |
| `@promise` | Promise 式异步函数 | `await func(args)` |
| （无注解） | 同步函数 | `func(args)` |

---

## 第一步：定义接口

**File: `idl/async.taihe`**

```rust
// 使用 @rename 重命名使异步函数名与 .d.ts 中的声明一致
@rename("add")
@async function addWithCallback(a: i32, b: i32): i32;

@rename("add")
@promise function addReturnsPromise(a: i32, b: i32): i32;

function addSync(a: i32, b: i32): i32;
```

### 注解说明

| 注解 | 作用 | 状态 |
|------|------|------|
| `@async` | 生成回调式异步版本 | ✅ 推荐 |
| `@promise` | 生成 Promise 式异步版本 | ✅ 推荐 |
| `@rename("name")` | 重命名 ArkTS 侧的函数名 | ✅ 推荐 |
| `@gen_async("name")` | 生成额外的异步函数 | ⚠️ 废弃 |
| `@gen_promise("name")` | 生成额外的 Promise 函数 | ⚠️ 废弃 |

## 第二步：实现 C++ 代码

**File: `author/src/async.impl.cpp`**

```cpp
#include "async.impl.hpp"

using namespace taihe;

// 按同步方式实现即可
int32_t addSync(int32_t a, int32_t b) {
    return a + b;
}

// 导出时可以复用同一实现
TH_EXPORT_CPP_API_addWithCallback(addSync);
TH_EXPORT_CPP_API_addReturnsPromise(addSync);
TH_EXPORT_CPP_API_addSync(addSync);
```

> **关键点**：C++ 侧按同步方式实现，Taihe 自动处理异步包装。

## 第三步：生成的 ArkTS 代码

**File (Generated): `generated/async.ets`**

```typescript
// 回调式异步函数
export function addWithCallback(a: int, b: int, callback: AsyncCallback<int>): void {
    taskpool.execute((): int => {
        return _taihe_addWithCallback_native(a, b);
    })
    .then((ret: Any): void => {
        callback(null, ret as int);
    })
    .catch((ret: Any): void => {
        callback(ret as BusinessError, undefined);
    });
}

// Promise 式异步函数
export function addReturnsPromise(a: int, b: int): Promise<int> {
    return new Promise<int>((resolve, reject): void => {
        taskpool.execute((): int => {
            return _taihe_addReturnsPromise_native(a, b);
        })
        .then((ret: Any): void => {
            resolve(ret as int);
        })
        .catch((ret: Any): void => {
            reject(ret as Error);
        });
    });
}

// 同步函数
export function addSync(a: int, b: int): int {
    return _taihe_addSync_native(a, b);
}

// 重载导出
export overload add {
    addWithCallback,
    addReturnsPromise,
}
```

## 第四步：编译运行

```sh
taihe-tryit test -u sts cookbook/async -Carkts:keep-name
```

> **注意**：默认情况下，Taihe IDL 中的函数名会转换为小驼峰命名。使用 `-Carkts:keep-name` 保持原名。

## 使用示例

**File: `user/main.ets`**

```typescript
import * as async_test from "async";

loadLibrary("async");

async function main() {
    // 同步调用
    console.log("addSync: ", async_test.addSync(1, 2));  // 3
    
    // 回调式异步调用
    async_test.add(10, 20, (error: BusinessError | null, data?: int) => {
        if (error !== null && error.code !== 0) {
            console.log("Error:", error);
        } else {
            console.log("Async result:", data);  // 30
        }
    });
    
    // Promise 式异步调用
    try {
        let result = await async_test.add(1, 2);
        console.log("Promise result:", result);  // 3
    } catch (error) {
        console.error("Error:", error);
    }
}
```

**输出：**

```
addSync:  3
Async result: 30
Promise result: 3
```

---

## 接口方法的异步版本

`@async` 和 `@promise` 同样适用于接口方法：

**File: `idl/async.taihe`**

```rust
interface IStringHolder {
    @rename("getString")
    @async getStringWithCallback(): String;

    @rename("getString")
    @promise getStringReturnsPromise(): String;

    getStringSync(): String;

    @rename("setString")
    @async setStringWithCallback(a: String): void;
    
    @rename("setString")
    @promise setStringReturnsPromise(a: String): void;
    
    setStringSync(a: String): void;
}
```

---

## 注解语法补充

Taihe 注解的通用规则：

| 语法 | 作用域 |
|------|--------|
| `@annotation` | 作用于下一个元素 |
| `@!annotation` | 作用于当前词法空间 |
| `@annotation("param")` | 带参数的注解 |
| `@annotation` | 无参数时可省略括号 |

**示例：**

```rust
@foobar struct Foo {}
// 等价于
struct Foo { @!foobar }
```

---

## 相关文档

- [Callback 回调](../callback/README.md) - 回调函数模式
- [Interface 接口](../interface/README.md) - 接口定义
