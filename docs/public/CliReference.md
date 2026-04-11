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

代码生成后端决定了 `taihec` 会生成哪些代码文件。后端之间存在依赖关系，工具会自动根据配置的后端来递归地启用所需的其它后端，生成完整的代码。

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

| 语言类型  | `--user` 参数 | 说明 |
|-----------|---------------|------|
| C++       | `cpp`         | C++ 消费者直接调用 C++ 实现 |
| ArkTS-STA | `sts`         | 通过 ANI 桥接调用 C++ 实现 |
| ArkTS-DYN | `ts`          | 通过 NAPI 桥接调用 C++ 实现 |

> 更多语言支持（如 Kotlin 等）将在后续版本中添加。

### 使用示例

使用 `taihe-tryit` 进行完整的测试项目创建、代码生成、编译和运行流程如下（以 C++ 用户侧为例）：

假如要在 `test/my_new_project` 目录下创建一个新的测试项目，首先运行以下命令：

```sh
taihe-tryit create --user cpp test/my_new_project
```

执行上述命令后，`test/my_new_project` 目录下将会生成包括 `idl/`、`author/`、`user/` 等子目录的项目结构。用户可以在 `idl/` 目录下编写 `.taihe` 文件描述想要定义的接口。

接下来，运行以下命令生成桥接代码：

```sh
taihe-tryit generate --user cpp test/my_new_project
```

生成完成后，`test/my_new_project/generated/` 目录下将会包含根据 IDL 文件生成的 C++ 头文件和源文件，其中 `temp/` 子目录下的文件是实现模板，供开发者参考。开发者可以根据具体需要，将模板文件复制到 `author/src/` 目录下进行修改和组织。

> 注意：`temp/` 目录下的文件为接口实现的**模板框架**，之所以设计为此形式而非直接生成到 `author/`，是为了让开发者完全掌控业务代码的实现，例如用户可能希望按照自己的项目结构来组织这些文件的命名、结构与位置；此外，当在 `idl/` 中修改或新增接口定义时，用户可以根据实际需要选择性地将模板文件中的新增或修改部分复制到 `author/`，而不必每次都覆盖整个 `author/` 目录，从而更好地实现增量适配和接口演进。

最后，运行以下命令编译并运行测试：

```sh
taihe-tryit test --user cpp test/my_new_project
```

需要注意的是，以上命令会先重新执行代码生成步骤（相当于先重新执行一遍 `generate` 模式）以确保生成的代码与 IDL 中的接口定义保持同步。如果用户希望手动修改生成的代码（例如添加打印日志等调试信息）且不被自动覆盖，可以运行 `build` 模式来仅编译和运行而不重新生成：

```sh
taihe-tryit build --user cpp test/my_new_project
```

---

## 相关文档

- [Taihe IDL 语言规范](spec/IdlReference.md)
- [Taihe C++ 使用指南](backend-cpp/CppUsageGuide.md)
- [ANI/ArkTS 快速入门](backend-ani/AniQuickStart.md)
- [NAPI/ArkTS 快速入门](backend-napi/NapiQuickStart.md)
