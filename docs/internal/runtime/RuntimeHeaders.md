# 运行时头文件架构与规格

## 背景

### Taihe 的理想使用场景

Taihe 的设计目标是将作者侧（接口实现）和用户侧（接口使用）完全分离，通过中间的 C ABI 层作为二进制边界，从而实现作者侧和用户侧的任意模块化组合。理想情况下，Taihe 生成的作者侧桥代码和用户侧桥代码以统一的 Taihe ABI 为界严格分离：

```
  作者侧接口实现
→ 自动生成的作者侧桥代码
→ Taihe ABI (二进制边界)
→ 自动生成的用户侧桥代码
→ 用户侧接口调用
```

在这一模型中，作者只需要面对 Taihe 的核心类型抽象，不需要知道也不应该知道上层消费语言是什么。

### 当前的实际使用场景

然而，在当前 Taihe 主要面向的 ArkTS 1.2 接口改造场景下，作者侧和用户侧并不以 Taihe ABI 作为二进制边界，而是以 ANI 作为实际的二进制边界：

```
  (1) C++ Impl
→ (2) C++ Author Bridge (Auto generated)
→ (3) Taihe ABI (Auto generated)
→ (4) C++ User Bridge (Auto generated)
→ (5) ANI Bridge (Auto generated)
→ (6) ArkTS
```

其中 (5) ANI 是实际对外暴露的二进制接口，(3) Taihe ABI 在该场景下并不真正承担二进制分发的职能。作者侧用户在调用编译器时会同时启用 `cpp-author` 和 `ani-bridge` 两个后端，将 (1)(2)(3)(4) 的产物统一编译到同一个动态链接库中。

即：**架构上 (1) 是作者侧、(2) 是边界、(3)(4)(5) 是用户侧，但实际上 (1)(2)(3)(4) 都在同一个二进制里，(4) 才是真正的二进制边界。**

另一方面，SDK 作者在实现某些接口时不得不直接使用 ANI 工具接口（如 `ani_env`）来调用 ArkTS 反射 API，以利用 ANI 的高级特性（如设置错误、利用 `Opaque` 直接传递原始 ANI 引用等）。这导致了如下问题：

1. 作者侧代码与平台 SDK 产生耦合。
2. 需要为作者提供平台工具封装：Taihe 运行时为此提供了 `set_error()`、`get_env()`、`env_guard` 等 ANI 相关的便利函数，当前打包在 `runtime_ani.hpp` 中，并通过 `runtime.hpp` 作为统一入口暴露给作者。

### 核心矛盾

`runtime.hpp` 作为面向作者的统一运行时入口是当前妥协架构的产物：理想架构下，作者不需要任何平台相关的 API。但当前架构下，作者不可避免地要和平台交互，需要一个方便的入口。

与此同时，Taihe 计划引入 NAPI 后端，`runtime.hpp` 的平台绑定需要可切换，同时保持向后兼容（存量作者代码中通过 `runtime.hpp` 引入 ANI 相关平台运行时）。

## 运行时文件分层定义

### 总览

```
runtime/
├── include/
│   └── taihe/
│       ├── *.abi.h + *.hpp   ← 核心运行时
│       ├── runtime.hpp       ← 作者入口 facade
│       ├── runtime_ani.hpp   ← ANI 平台运行时
│       ├── runtime_napi.hpp  ← NAPI 平台运行时
│       └── platform/
│           ├── ani.hpp       ← ANI 桥基础设施
│           └── napi.hpp      ← NAPI 桥基础设施
└── src/
    ├── *.cpp
    ├── runtime_ani.cpp
    └── runtime_napi.cpp
```

### 第一层：核心运行时（平台无关）

| 项目 | 说明 |
|------|------|
| 文件 | `object.hpp`, `string.hpp`, `array.hpp`, `vector.hpp`, `map.hpp`, `set.hpp`, `optional.hpp`, `common.hpp` 等 |
| 依赖 | 仅依赖 C++ 标准库和对应的 `.abi.h` C 头文件 |
| 消费者 | 所有代码——生成代码、作者侧代码、运行时内部 |
| 内容 | Taihe 类型系统：`data_view`/`data_holder`、`string`/`string_view`、容器类型、ABI 类型映射模板（`as_abi`、`as_param`）、对象模型（`impl_view`/`impl_holder`）等 |

### 第二层：平台运行时（无 codegen 依赖）

| 项目 | 说明 |
|------|------|
| 文件 | `runtime_*.hpp` |
| 依赖 | 核心运行时、平台 SDK |
| 消费者 | `platform/*.hpp`、`runtime.hpp` |
| 内容 | 平台生命周期管理和基础工具 |

以 `runtime_ani.hpp` 为例，当前提供了以下功能：

| 接口 | 用途 |
|------|------|
| `set_vm(ani_vm*)` / `get_vm()` | 全局 VM 实例管理 |
| `get_env()` | 获取当前线程的 `ani_env*` |
| `env_guard` | RAII guard，自动 attach/detach 当前线程 |
| `set_error(msg)` / `set_business_error(code, msg)` | 向 ANI 层抛出错误 |
| `reset_error()` / `has_error()` | 错误状态查询与重置 |

**为什么不合并到 `platform/*.hpp`：** `runtime_*.hpp` 没有 codegen 依赖，可以独立编译为运行时库的一部分。`platform/ani.hpp` 依赖 codegen 输出（`taihe.platform.ani.proj.hpp`）。将此层合并到第三层会导致编译基础运行时库也需要先运行 codegen，造成不必要的构建顺序耦合。

### 第三层：平台桥基础设施（依赖 codegen 输出）

| 项目 | 说明 |
|------|------|
| 文件 | `platform/ani.hpp`；未来 `platform/napi.hpp` |
| 依赖 | 核心运行时、平台运行时、基于 stlib 的 codegen 产物（如 `taihe.platform.ani.proj.hpp`） |
| 消费者 | 仅限生成的桥代码（`*.ani.cpp` 等） |
| 内容 | 类型转换、反射工具、引用管理、对象模型特化 |

以 `platform/ani.hpp` 为例，当前提供：

| 分类 | 内容 |
|------|------|
| 类型转换 | `from_ani_t<T>` / `into_ani_t<T>` 模板：ANI 类型与 Taihe 类型之间的转换 |
| 引用管理 | `sref_guard`（全局静态引用）、`dref_guard`（全局动态引用，RAII 释放） |
| 反射工具 | `ani_find_module()`, `ani_find_class()`, `ani_find_method()` 等 |
| 反射缓存 | `TH_ANI_FIND_*` 宏：带缓存优化的 ANI 反射接口 |
| 对象模型特化 | `same_impl_t<AniRefGuard>` / `hash_impl_t<AniRefGuard>`：为 ANI 引用类型提供相等性比较和哈希 |

**关于 `weak::AniObject` 的依赖：** `platform/ani.hpp` 中的 `same_impl_t` 特化使用了 `taihe::platform::ani::weak::AniObject`。这是从 `taihe.platform.ani.taihe` IDL（定义了 `interface AniObject { getGlobalReference(): Opaque; }`）生成的 C++ 弱引用投影类型，用于从通用的 `data_view` 中尝试解包出底层 ANI 对象引用，从而调用 `env->Reference_Equals()` 实现 ANI 语义的相等性比较。这是第三层必须依赖 codegen 的根本原因，也是第二层和第三层不能合并的硬性技术约束。

### `runtime.hpp`：作者侧入口 facade

| 项目 | 说明 |
|------|------|
| 文件 | `runtime.hpp` |
| 依赖 | 平台运行时（`runtime_*.hpp`） |
| 消费者 | 作者侧用户代码（`*.impl.cpp`） |
| 内容 | 平台选择和兼容层 |

该文件是当前妥协架构的产物，与特定平台耦合的接口作者在其作者侧接口定义代码（C++ Impl）中，通过它引入平台相关的便利工具（如 ANI 的错误管理、环境获取等）。

该文件通过预处理宏转发到具体平台的运行时实现：

```cpp
#ifndef TAIHE_RUNTIME_HPP
#define TAIHE_RUNTIME_HPP

#ifdef TAIHE_USE_ANI_RUNTIME
#include "runtime_ani.hpp"
#endif

#ifdef TAIHE_USE_NAPI_RUNTIME
#include "runtime_napi.hpp"
#endif

#endif  // TAIHE_RUNTIME_HPP
```

## include 规则总结

| 消费者 | 应 include | 不应 include |
|--------|-----------|-------------|
| 作者侧用户代码（`*.impl.cpp`） | `taihe/runtime.hpp` | `taihe/platform/ani.hpp` |
| 编译器生成的桥代码 | `taihe/platform/*.hpp` | `taihe/runtime.hpp` |
| `platform/*.hpp` 内部 | `taihe/runtime_*.hpp` | `taihe/runtime.hpp` |
| `runtime.hpp` 内部 | `taihe/runtime_*.hpp`（按宏选择） | `taihe/platform/*.hpp` |

## 演进路线

当架构演进到作者侧与用户侧真正分离时：

1. 作者侧动态库不再包含桥代码，不再需要平台 SDK 依赖。
2. `runtime.hpp` 不再有意义，因为用户侧不再需要通过它来引入平台相关工具。
3. `runtime_ani.hpp` 在文件系统中保留，但**从面向用户的 API 退化为内部基础设施**，仅被 `platform/ani.hpp` 和生成的桥代码依赖。
4. `platform/ani.hpp` 定位不变，继续作为生成代码的专用基础设施。
