# Taihe 基本使用文档

本文档介绍 Taihe 命令行工具的使用方法。

## Taihe 命令行使用方法

Taihe 提供了 `taihec` 和 `taihe-tryit` 两个命令行工具，分别用于代码生成和自测试。

### `taihec`

`taihec` 仅生成代码。

```sh
taihec [taihe_files ...] [options ...]
```

- 输入：Taihe IDL 文件
- 输出：生成文件

_注：`taihe_files` 可以是一个或多个 Taihe IDL 文件，也可以使用通配符（例如 `path/to/idl/*.taihe`）来指定多个文件。_

#### 命令行选项

| 参数                                       | 简写                               | 说明                                                                        |
| ------------------------------------------ | ---------------------------------- | --------------------------------------------------------------------------- |
| `--output <path>`                          | `-O<path>`                         | 指定生成的目标文件存放目录（默认：`taihe-generated`）                       |
| `--generate <backend>`                     | `-G<backend>`                      | 指定要启用的代码生成后端，如 `abi-header`、`abi-source`、`c-author` 等      |
| `--build <build-system>`                   | `-B<build-system>`                 | 指定构建系统类型，目前支持 `cmake`（生成 `CMakeLists.txt`）                 |
| `--codegen <namespace>:<config>[=<value>]` | `-C<namespace>:<config>[=<value>]` | 额外的代码生成配置项，例如 `sts:keep-name`、`arkts:module-prefix=prefix` 等 |
| `--version`                                |                                    | 打印版本信息                                                                |
| `--help`                                   | `-h`                               | 帮助信息                                                                    |

#### 代码生成后端

代码生成后端决定了 `taihec` 会生成哪些代码文件。后端之间存在依赖关系，工具会自动根据配置的后端来递归地启用所需的其他后端，生成完整的代码。

| Backend        | 说明                                              | 依赖                       |
| -------------- | ------------------------------------------------- | -------------------------- |
| `abi-header`   | 生成 Taihe C ABI 头文件，包括类型声明，函数声明等 | 无                         |
| `abi-source`   | 生成 Taihe C ABI 源文件，包含必要的符号定义       | `abi-header`               |
| `c-author`     | 生成 C 语言提供者侧的接口导出宏以及模板代码       | `abi-source`               |
| `cpp-common`   | 生成 C++ 接口提供者和消费者侧的公共代码           | `abi-header`               |
| `cpp-author`   | 生成 C++ 接口提供者侧的接口导出宏以及模板代码     | `cpp-common`, `abi-source` |
| `cpp-user`     | 生成 C++ 接口消费者侧所需的所有代码               | `cpp-common`               |
| `ani-bridge`   | 生成 ANI 及 ArkTS 1.2 用户侧的桥接代码            | `cpp-user`                 |
| `pretty-print` | 将 Taihe IDL 文件格式化输出                       | 无                         |

#### 代码生成配置

| Codegen Config                 | 说明                                                                                                                     |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| `sts:keep-name`                | 保持生成的代码中的函数和方法名称与 Taihe IDL 文件中的名称一致，若不使用此选择则会默认将 Taihe IDL 文件中的名称首字母小写 |
| `arkts:module-prefix=<prefix>` | 指定生成的 ArkTS 对应的模块名，该配置会影响生成符号的 ANI 签名                                                           |
| `arkts:path-prefix=<prefix>`   | 指定生成的 ArkTS 对应的路径前缀，该配置会影响生成符号的 ANI 签名                                                         |

_注：DevEco 用户必须指定 `arkts:module-prefix` 与 `arkts:path-prefix`_

#### 使用示例

以下是一个 `taihec` 的基本使用示例：

```sh
taihec test/ani_test/idl/*.taihe -Otest/ani_test/generated -Gani-bridge -Gcpp-author -Carkts:module-prefix=<module_name> -Carkts:path-prefix=<pkg_name> -Bcmake  # 生成用户自己在 IDL 中定义的接口的 ANI 桥接代码，以及 C++ 实现模板等
```

### `taihe-tryit`

`taihe-tryit` 是一个 Taihe 内置的高度集成的自测试和验证工具，能够一键创建项目、生成代码、编译并运行测试。适合快速原型开发、学习和验证一个完整的样例。

```sh
taihe-tryit [mode] [test_dir] [options ...]
```

#### 模式

`taihe-tryit` 支持多种模式，主要介绍 `create`、`generate`、`build`、`test` 几种：

- `create`
  用于创建一个新的测试样例目录，包含必要的目录结构和文件，例如：

  ```sh
  taihe-tryit create --user sts path/to/demo/dir
  ```

- `generate`
  用于生成桥接代码，例如：

  ```sh
  taihe-tryit generate --user sts path/to/demo/dir
  ```

- `build`
  不生成代码，将已有的代码进行编译并运行，用于生成了代码后，对生成的代码进行修改的场景，例如：

  ```
  taihe-tryit build --user sts path/to/demo/dir
  ```

- `test`
  生成代码，并编译运行，该命令等价于分别执行 `generated` 和 `build`，用于快速验证一个完整的样例，例如：
  ```
  taihe-tryit test --user sts path/to/demo/dir
  ```

#### 支持的选项

| 参数                                       | 简写                               | 说明                                                                | 可用模式           |
| ------------------------------------------ | ---------------------------------- | ------------------------------------------------------------------- | ------------------ |
| `--verbose`                                | `-v`                               | 输出详细的日志信息，便于调试                                        | 所有模式           |
| `--user <user>`                            | `-u <user>`                        | 必要，选择消费者侧的语言类型，支持 `sts`（ArkTS 1.2）、`cpp`（C++） | 所有模式           |
| `--optimization {0,1,2,3}`                 | `-O{0,1,2,3}`                      | 指定编译器的优化级别，默认为 `0`                                    | `build`、`test`    |
| `--codegen <namespace>:<config>[=<value>]` | `-C<namespace>:<config>[=<value>]` | 同 `taihec`，额外的代码生成配置项，例如 `sts:keep-name` 等          | `generate`、`test` |

#### 使用流程

下面我们以一个 ArkTS 1.2 代码调用 C++ 实现的项目为例，展示其标准流程。

1. 用于 `taihe-tryit` 的标准目录结构如下，你可以运行 `taihe-tryit create --user sts path/to/demo` 来自动生成一个最简单的样例目录：

   ```
   demo
   ├── idl                             # Taihe IDL 文件目录
   │   └── hello.taihe
   ├── author                          # C++ 接口提供者侧代码目录
   |   ├── include
   │   └── src
   |        └── hello.impl.cpp         # hello.taihe 的 C++ 实现
   |        └── ani_constructor.cpp    # ani 注册文件
   └── user                            # 接口消费者侧代码目录
       └── main.ets                    # 测试入口
   ```

2. 执行 `taihe-tryit generate --user sts path/to/demo` 后，会在 `path/to/demo` 中生成一个 `generated` 目录，包含生成的代码和头文件。也可以尝试修改 `hello.taihe`，按照 [Taihe 语言规范](../spec/IdlReference.md)编写自己的接口描述文件并进行生成。

   ```
   generated
   ├── @ohos.base.ets                   # 用于导入 BusinessError，用户上库不需要
   ├── hello.ets
   ├── include                          # 生成的 C/C++ 头文件目录
   │   ├── hello.abi.h
   │   ├── hello.impl.hpp
   │   ├── hello.proj.hpp
   │   ├── hello.user.hpp               # 这几个是 C++ 提供方和消费方所需头文件，具体功能见 CppUserDoc.md
   │   ├── hello.ani.hpp                # 用于注册 ANI Native 接口的 ANIRegister 所在头文件
   |   ├── taihe.platform.ani.abi.h
   │   ├── taihe.platform.ani.proj.hpp  # Taihe 标准库对应的头文件
   │   └── ...
   ├── src                              # 自动生成的源文件，会被编译进 C++ 提供方的动态链接库中
   │   ├── hello.abi.c
   │   ├── hello.ani.cpp
   │   └── taihe.platform.ani.abi.c
   └── temp                             # 用于方便用户使用的模板文件，用户可以复制这些文件到 author/src 目录下进行修改
       ├── ani_constructor.cpp
       └── hello.impl.cpp
   ```

3. 用户可以在 `author` 目录下编写 C++ 提供者侧的代码，可以参考 `generated/temp` 目录下的模板源码文件。然后在 `user` 目录下编写 ArkTS 消费者侧的代码，应用入口应该是 `main.ets` 文件。

4. 完成后，运行 `taihe-tryit build --user sts path/to/demo` 来编译生成动态库及用户侧程序并运行。
