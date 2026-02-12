# Taihe 命令行工具参考

本文档介绍 Taihe 命令行工具的使用方法。

## 概述

Taihe 提供了两个命令行工具：

- **`taihec`**：核心编译器，用于解析 Taihe IDL 文件并生成目标语言代码
- **`taihe-tryit`**：集成测试工具，用于快速创建、生成、编译和运行测试项目

---

## `taihec`

`taihec` 是 Taihe 的核心编译器工具，用于解析 Taihe IDL 文件并编译为目标语言的代码。支持选择任意多种代码生成后端，生成适用于不同场景的代码。

### 基本用法

```sh
taihec [taihe_files ...] [options ...]
```

- `taihe_files` 可以是一个或多个 Taihe IDL 文件，也可以使用通配符（例如 `path/to/idl/*.taihe`）来指定多个文件。
- `options` 用于指定代码生成的各种选项，详见下表。

### 命令行选项

| 参数                                       | 简写                               | 说明 |
|--------------------------------------------|------------------------------------|------|
| `--output <path>`                          | `-O<path>`                         | 指定生成的目标文件存放目录（如缺省则默认生成在 `taihe-generated` 目录下） |
| `--generate <backend>`                     | `-G<backend>`                      | 指定要启用的代码生成后端，如 `abi-header`、`abi-source`、`c-author` 等 |
| `--build <build-system>`                   | `-B<build-system>`                 | 指定构建系统类型，目前支持 `cmake`（生成 `CMakeLists.txt`） |
| `--codegen <namespace>:<config>[=<value>]` | `-C<namespace>:<config>[=<value>]` | 额外的代码生成配置项（详见各后端文档） |
| `--version`                                | 无                                 | 打印版本信息 |
| `--help`                                   | `-h`                               | 帮助信息 |

### 代码生成后端

代码生成后端决定了 `taihec` 会生成哪些代码文件。后端之间存在依赖关系，工具会自动根据配置的后端来递归地启用所需的其他后端，生成完整的代码。

#### 通用后端

| Backend        | 依赖           | 说明 |
|----------------|----------------|------|
| `abi-header`   | 无             | 生成 Taihe C ABI 头文件，包括类型声明、函数声明等 |
| `abi-source`   | `abi-header`   | 生成 Taihe C ABI 源文件，包含必要的符号定义 |
| `pretty-print` | 无             | 将 Taihe IDL 文件格式化输出 |

#### C/C++ 后端

| Backend        | 依赖                       | 说明 |
|----------------|----------------------------|------|
| `c-author`     | `abi-source`               | 生成 C 语言提供者侧的接口导出宏以及模板代码 |
| `cpp-common`   | `abi-header`               | 生成 C++ 接口提供者和消费者侧的公共代码 |
| `cpp-author`   | `cpp-common`, `abi-source` | 生成 C++ 接口提供者侧的接口导出宏以及模板代码 |
| `cpp-user`     | `cpp-common`               | 生成 C++ 接口消费者侧所需的所有代码 |

#### ANI/ArkTS 后端

| Backend        | 依赖       | 说明 |
|----------------|------------|------|
| `ani-bridge`   | `cpp-user` | 生成 ANI 及 ArkTS 用户侧的桥接代码 |

> 更多后端（如 NAPI/ArkTS、Kotlin 等）将在后续版本中支持。

### 使用示例

**生成 C++ 作者侧和用户侧代码：**

```sh
taihec idl/*.taihe -Ogenerated -Gcpp-author -Gcpp-user -Bcmake
```

**生成 ANI/ArkTS 桥接代码：**

```sh
taihec idl/*.taihe -Ogenerated -Gani-bridge -Gcpp-author -Bcmake
```

---

## `taihe-tryit`

`taihe-tryit` 是一个 Taihe 内置的高度集成的自测试和验证工具，能够一键创建项目、生成代码、编译并运行测试。适合快速原型开发、学习和验证一个完整的样例。

### 基本用法

```sh
taihe-tryit [mode] [test_dir] [options ...]
```

### 模式

| 模式       | 说明 |
|------------|------|
| `create`   | 创建一个新的测试样例目录，包含必要的目录结构和文件 |
| `generate` | 根据 IDL 文件生成桥接代码 |
| `build`    | 编译已有代码并运行（不重新生成） |
| `test`     | 生成代码、编译并运行（等价于 `generate` + `build`） |

### 支持的选项

| 参数                                       | 简写                               | 可用模式           | 说明 |
|--------------------------------------------|------------------------------------|--------------------|------|
| `--verbose`                                | `-v`                               | 所有模式           | 输出详细的日志信息，便于调试 |
| `--user <user>`                            | `-u <user>`                        | 所有模式           | **必需**，选择消费者侧的语言类型 |
| `--optimization {0,1,2,3}`                 | `-O{0,1,2,3}`                      | `build`, `test`    | 指定编译器的优化级别，默认为 `0` |
| `--codegen <namespace>:<config>[=<value>]` | `-C<namespace>:<config>[=<value>]` | `generate`, `test` | 额外的代码生成配置项 |

### 支持的用户侧语言

| 语言类型 | `--user` 参数 | 说明 |
|----------|---------------|------|
| ArkTS    | `sts`         | 通过 ANI 桥接调用 C++ 实现 |
| C++      | `cpp`         | C++ 消费者直接调用 C++ 实现 |

> 更多语言支持（如 Kotlin 等）将在后续版本中添加。

### 使用示例

**创建新项目：**

```sh
taihe-tryit create --user sts path/to/demo
```

**生成代码：**

```sh
taihe-tryit generate --user sts path/to/demo
```

**编译并运行：**

```sh
taihe-tryit test --user sts path/to/demo
```

---

## 相关文档

- [Taihe IDL 语言规范](spec/IdlReference.md)
- [ANI/ArkTS 快速入门](backend-ani/AniQuickStart.md)
- [C++ 使用指南](backend-cpp/CppUsageGuide.md)
