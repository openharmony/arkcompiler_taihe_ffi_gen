# ANI/ArkTS 快速入门

本文档介绍如何使用 Taihe 将 C++ 实现暴露给 ArkTS 调用。

> **前置知识**：建议先阅读 [命令行工具参考](../CliReference.md) 了解 `taihec` 和 `taihe-tryit` 的基本用法。

## 概述

ANI（ArkTS Native Interface）是 ArkTS 调用原生代码的桥接机制。Taihe 的 `ani-bridge` 后端可以自动生成 ANI 桥接代码，让 ArkTS 代码能够调用 C++ 实现。

## 代码生成配置

使用 `ani-bridge` 后端时，支持以下代码生成配置项：

| 配置项                         | 说明 |
|--------------------------------|------|
| `sts:keep-name`                | 保持生成的代码中的函数和方法名称与 Taihe IDL 文件中的名称一致。若不使用此选项，则默认将 IDL 中的名称首字母小写 |
| `arkts:module-prefix=<prefix>` | 指定生成的 ArkTS 对应的模块名，该配置会影响生成符号的 ANI 签名 |
| `arkts:path-prefix=<prefix>`   | 指定生成的 ArkTS 对应的路径前缀，该配置会影响生成符号的 ANI 签名 |

> ⚠️ **注意**：DevEco 用户必须指定 `arkts:module-prefix` 与 `arkts:path-prefix`。

### 使用示例

```sh
taihec idl/*.taihe -Ogenerated -Gani-bridge -Gcpp-author \
    -Carkts:module-prefix=mymodule \
    -Carkts:path-prefix=com.example \
    -Bcmake
```

---

## 使用 `taihe-tryit` 快速上手

下面我们以一个完整的示例展示如何使用 `taihe-tryit` 快速创建、生成和运行一个 ArkTS 调用 C++ 的项目。

### 1. 创建项目

运行以下命令创建一个新的样例目录：

```sh
taihe-tryit create --user sts path/to/demo
```

生成的标准目录结构如下：

```
demo/
├── idl/                            # Taihe IDL 文件目录
│   └── hello.taihe
├── author/                         # C++ 接口提供者侧代码目录
│   ├── include/
│   └── src/
│       ├── hello.impl.cpp          # hello.taihe 的 C++ 实现
│       └── ani_constructor.cpp     # ANI 注册文件
└── user/                           # 接口消费者侧代码目录
    └── main.ets                    # 测试入口
```

### 2. 生成代码

运行以下命令生成桥接代码：

```sh
taihe-tryit generate --user sts path/to/demo
```

生成的 `generated` 目录结构如下：

```
generated/
├── hello.ets                       # ArkTS 桥接代码
├── include/                        # 生成的 C/C++ 头文件目录
│   ├── hello.abi.h                 # C ABI 头文件
│   ├── hello.proj.hpp              # C++ 类型投影
│   ├── hello.impl.hpp              # C++ 提供方所需头文件
│   ├── hello.user.hpp              # C++ 消费方所需头文件
│   ├── hello.ani.hpp               # ANI 注册函数所在头文件
│   ├── taihe.platform.ani.*.hpp    # Taihe 标准库头文件
│   └── ...
├── src/                            # 自动生成的源文件
│   ├── hello.abi.c
│   ├── hello.ani.cpp
│   └── taihe.platform.ani.abi.c
└── temp/                           # 模板文件（可复制到 author/src 修改）
    ├── ani_constructor.cpp
    └── hello.impl.cpp
```

也可以尝试修改 `hello.taihe`，按照 [Taihe IDL 语言规范](../spec/IdlReference.md) 编写自己的接口描述文件并进行生成。

### 3. 实现接口

参考 `generated/temp` 目录下的模板文件，在 `author/src` 目录下编写 C++ 实现代码。

**示例 IDL（`idl/hello.taihe`）：**

```
function add(a: i32, b: i32): i32;
```

**示例实现（`author/src/hello.impl.cpp`）：**

```cpp
#include "hello.impl.hpp"

int32_t add(int32_t a, int32_t b) {
    return a + b;
}

TH_EXPORT_CPP_API_add(add);
```

**示例测试（`user/main.ets`）：**

```typescript
import * as hello from "hello";

loadLibrary("hello");

function main() {
    let result = hello.add(1, 2);
    console.log("1 + 2 = " + result);
}
```

### 4. 编译运行

运行以下命令编译并执行测试：

```sh
taihe-tryit test --user sts path/to/demo
```

或者分步执行：

```sh
# 仅生成代码
taihe-tryit generate --user sts path/to/demo

# 仅编译运行（不重新生成）
taihe-tryit build --user sts path/to/demo
```

---

## 相关文档

- [命令行工具参考](../CliReference.md) - `taihec` 和 `taihe-tryit` 完整参数说明
- [Taihe IDL 语言规范](../spec/IdlReference.md) - IDL 语法和语义规则
- [ANI 注解参考](../spec/supported-attributes/AniAttributes.md) - ANI 后端特有的注解
- [ANI 生成代码解析](AniGeneratedCode.md) - 深入理解生成代码的结构和调用链
- [C++ 使用指南](../backend-cpp/CppUsageGuide.md) - C++ 类型和 API 的详细说明
