# 运行时架构知识

本文只记录 Taihe 运行时的文件分层和依赖方向。数据类型、内存管理和调用协议见 `Runtime_Type_Protocols_Knowledge_Base_CN.md`。

## 文件分层

| 层级 | 文件 | 职责 | 直接依赖 |
| --- | --- | --- | --- |
| 公共基础库 | `common.h`, `common.hpp` | C 基础定义、断言、`as_abi`、`as_param` 等公共模板 | C/C++ 标准库；`common.hpp` 依赖 `common.h`。 |
| 面向对象基础库 | `object.abi.h`, `object.hpp` | 数据块、运行时类型信息、引用计数、持有/借用和接口实现工具 | 公共基础库。 |
| 调用基础库 | `expected.hpp`, `invoke.hpp` | C++ 调用结果、ABI 值转换和函数调用适配 | 公共基础库；`invoke.hpp` 还依赖面向对象基础库。 |
| 数据类型与容器 | 类型对应的 `*.abi.h`, `*.hpp` | 定义字符串、数组、可选值、异步值、回调和其他容器的 ABI 与 C++ 类型 | 公共基础库；接口化类型可依赖调用基础库和面向对象基础库。 |
| 平台运行时 | `runtime_*.hpp`, `runtime_*.cpp` | 平台环境、错误状态、平台句柄生命周期和基础工具 | 基础库和对应平台的 SDK；不得依赖生成代码。 |
| 作者入口 | `runtime.hpp` | 按构建配置选择一个 `runtime_*.hpp` | 只依赖平台运行时。 |
| 平台桥 | `platform/*.hpp` | 供生成桥代码使用的类型转换、反射、引用管理和对象特化 | 依赖平台运行时、根据标准库生成的头文件。 |

## 约束规则

- 第一至第四层不得依赖平台 SDK 或生成代码，否则通用运行时无法独立构建。
- `runtime_*.hpp` 和 `runtime_*.cpp` 不得依赖生成代码；需要生成声明的能力只能放入 `platform/*.hpp`。
- `runtime.hpp` 只负责选择平台运行时，不要加入类型转换、反射或对象协议。
- 作者侧实现只包含 `runtime.hpp`；不要直接包含 `platform/*.hpp`，后者只供生成的桥代码使用。
- 容器和生成投影必须复用公共基础、调用基础和对象基础；不要复制 `as_abi`、引用计数或调用适配规则。
- 不要在公共头中引入只被单个实现文件使用的依赖，否则会扩大所有消费者的编译范围。

## 修改前检查

| 问题 | 决策 |
| --- | --- |
| 新代码属于上表哪一层？ | 按文件职责选择唯一层，不要同时归入多种分类。 |
| 是否定义通用类型、调用或对象协议？ | 进入第一至第四层，并保持平台无关。 |
| 是否只需要平台 SDK，不需要生成声明？ | 进入 `runtime_*.hpp` / `runtime_*.cpp`。 |
| 是否需要标准库或其他生成声明？ | 只能进入 `platform/*.hpp` 及其生成代码消费者。 |
| 是否面向作者侧实现？ | 通过 `runtime.hpp` 暴露，不要泄漏平台桥头文件。 |

## 代码和测试

| 主题 | 锚点 |
| --- | --- |
| 公共、调用、对象和容器层 | `runtime/include/taihe/`, `runtime/src/` |
| 平台运行时与作者入口 | `runtime/include/taihe/runtime*.hpp`, `runtime/src/runtime_*.cpp` |
| 平台桥 | `runtime/include/taihe/platform/` |
| 头文件设计 | `docs/internal/runtime/RuntimeHeaders.md` |
| 平台和构建验证 | `test/`, `CMakeLists.txt` |