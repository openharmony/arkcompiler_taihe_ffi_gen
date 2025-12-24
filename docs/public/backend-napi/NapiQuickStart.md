# Taihe Napi 快速入门

**用户在使用 Taihe 开发 Napi 桥接代码时，请专注参考以下核心文档：**

- [Taihe IDL 语言规范](../spec/IdlReference.md)

- [Taihe C++ 数据结构用法](../backend-cpp/CppUsageGuide.md)

- [Taihe Napi 用户文档](./NapiUsageGuide.md)

*此外文档涉及不同后端，与本开发无关。*

## Taihe 命令行使用方法

Taihe 提供了 `taihec` 和 `taihe-tryit` 两个命令行工具，分别用于代码生成和自测试。

### `taihec`

`taihec` 仅生成代码。
```sh
taihec [taihe_files ...] [options ...]
```

- 输入：Taihe IDL 文件
- 输出：生成文件

*注：`taihe_files` 可以是一个或多个 Taihe IDL 文件，也可以使用通配符，例如 `path/to/idl/*.ohidl` 来指定多个文件。*

#### 命令行选项

| 参数 | 简写 | 说明 |
| ---- | ---- | ---- |
| `--output <path>` | `-O<path>` | 指定生成的目标文件存放目录（默认：`taihe-generated`） |
| `--generate <backend>` | `-G<backend>` | 指定要启用的代码生成后端，如 `abi-header`、`abi-source`、`c-author` 等 |
| `--build <build-system>` | `-B<build-system>` | 指定构建系统类型，目前支持 `cmake`（生成 `CMakeLists.txt`） |
| `--version` | | 打印版本信息 |
| `--help` | `-h` | 帮助信息 |

#### 代码生成后端

代码生成后端决定了 `taihec` 会生成哪些代码文件。后端之间存在依赖关系，工具会自动根据配置的后端来递归地启用所需的后端，生成完整的代码。

| Backend | 说明 | 依赖 |
| ------- | ---- | ---- |
| `abi-header` | 生成 Taihe C ABI 头文件，包括类型声明，函数声明等 | 无 |
| `abi-source` | 生成 Taihe C ABI 源文件，包含必要的符号定义 | `abi-header` |
| `c-author` | 生成 C 语言提供者测的接口导出宏以及模板代码 | `abi-source` |
| `cpp-common` | 生成 C++ 接口提供者和消费者侧的公共代码 | `abi-header` |
| `cpp-author` | 生成 C++ 接口提供者侧的接口导出宏以及模板代码 | `cpp-common`, `abi-source` |
| `cpp-user` | 生成 C++ 接口消费者侧的所需代码 | `cpp-common` |
| `napi-bridge` | 生成 Napi 相关的桥接代码 | `cpp-user` |
| `pretty-print` | 将 Taihe IDL 文件格式化输出 | 无 |

#### 使用示例

以下是一个 `taihec` 的基本使用示例：
```sh
taihec test/napi_string/idl/*.ohidl -Otest/napi_string/generated -Gnapi-bridge -Gcpp-author  # 生成用户自己在 IDL 中定义的接口的 NAPI 桥接代码，以及 C++ 实现模板等
```

### `taihe-tryit`

`taihe-tryit` 是一个 Taihe 内置的高度集成的自测试和验证工具，能够一键创建项目、生成代码、编译并运行测试。适合快速原型开发、学习和验证一个完整的样例。以下是 `taihe-tryit` 的基本用法：

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

| 参数                                       | 简写                               | 可用模式           | 说明 |
|--------------------------------------------|------------------------------------|--------------------|------|
| `--verbose`                                | `-v`                               | 所有模式           | 输出详细的日志信息，便于调试 |
| `--user <user>`                            | `-u <user>`                        | 所有模式           | 必要，选择消费者侧的语言类型，支持 `sts`, `cpp`, `ts` |
| `--optimization {0,1,2,3}`                 | `-O{0,1,2,3}`                      | `build`, `test`    | 指定编译器的优化级别，默认为 `0` |
| `--codegen <namespace>:<config>[=<value>]` | `-C<namespace>:<config>[=<value>]` | `generate`, `test` | 同 `taihec`，额外的代码生成配置项，例如 `sts:keep-name` 等 |

<small>*Taihe 生成 NAPI 桥接代码时暂不支持 `sts:keep-name` 选项，所有生成代码默认与 IDL 文件名保持一致。*</small>

## prebuilts 使用流程

注意，需基于已下载的最新 prebuilts。可直接使用 `taihec` 和 `taihe-tryit` 命令，例如：

```bash
//prebuilts/taihe/napi_taihe/taihe/bin/taihec xxx.ohidl \
  -O generated_dir/ \
  -G napi-bridge cpp-author

//prebuilts/taihe/napi_taihe/taihe/bin/taihe-tryit test --user ts path/to/demo/dir
```

## IDE 使用流程

下面以一个 memberTest 项目为例，展示其标准流程。

1. **准备工具**

   - 获取解压后的 Taihe 工具包
   - 存放路径可自定义（无特殊限制）

2. **编写 Taihe 文件**

   - **命名规则**：
     ```plaintext
     [a-zA-Z_][a-zA-Z0-9_.]*.ohidl
     ```
     - 正确示例：`member_test.ohidl`
     - 含特殊字符时需使用注解：
       ```rust
       @!namespace("@my.module")
       ```
   - 文件存放目录无限制
   - 内容规范详见[Taihe Napi 用户文档](./NapiUsageGuide.md)

3. **生成桥接代码**
   执行生成命令（参数说明）：

   ```bash
   taihec <输入.ohidl文件> -O <输出目录> -G napi-bridge cpp-author
   ```

   - **生成内容**：
     - Napi 桥接代码（C++）
     - `.d.ts` 声明文件（默认同原名，含 `@!namespace` 时按注解命名）
     - `.ts` 代理实现文件，只有用户需要（使用 `@!lib` 注解）时会生成，存储在 `//generated/proxy` 目录下，与 `.d.ts` 声明文件同名

   **实际用例**：

   ```bash
   ./taihe/napi_taihe/taihe/bin/taihec .memberTest/entry/src/main/idl/member_test.ohidl \
     -O .memberTest/entry/src/main/generated/ \
     -G napi-bridge cpp-author
   ```

   **生成目录结构**：

   ```tree
   base_dir/
   └── memberTest/
       └── entry/
           └── src/
               └── main/
                   ├── generated/
                   │   ├── include/  # 头文件
                   │   ├── src/       # 实现代码
                   │   ├── temp/      # 临时文件
                   │   ├── proxy/     # 代理 ts 实现文件（用户需要时生成）
                   |   └── member_test.d.ts   # 声明文件
                   └── idl/
                       └── member_test.ohidl  # 源文件
   ```

4. **书写 .cpp 文件**
   运行 taihec 命令会在 `memberTest/entry/src/main/generated/temp` 目录下生成 cpp 实现文件模板 `membertest_test.impl.cpp`，需要用户将其拷贝到存放实现文件的目录中并手动填写实现逻辑

5. **将生成文件加入编译流程**
   以 IDE 中内置的 CMakeLists.txt 文件为基础，需要进行以下修改：

   - Taihe 生成代码需使用 C++ 17 标准编译，需要在 CMakeLists.txt 文件中新增以下内容
     ```CMakeLists.txt
     set(CMAKE_CXX_STANDARD 17)
     set(CMAKE_CXX_STANDARD_REQUIRED True)
     ```
   - .cpp 实现文件和 Taihe 的 runtime 文件都需要加入编译，所以编译部分应修改为

     ```CMakeLists.txt
     add_library(entry SHARED
     membertest_test.impl.cpp
     ../generated/temp/napi_register.cpp
     ../generated/src/member_test.napi.cpp
     //base_dir/taihe/src/taihe/runtime/object.cpp
     //base_dir/taihe/src/taihe/runtime/string.cpp
     //base_dir/taihe/src/taihe/runtime/runtime_napi.cpp
     )

     target_include_directories(entry
     PUBLIC
     //base_dir/taihe/napi_taihe/taihe/include
     ../generated/include
     )
     ```

  - 需传递参数表示在编译 napi 代码

     ```CMakeLists.txt
     target_compile_definitions(entry PRIVATE USE_NAPI_RUNTIME=1)
     ```

可以使用命令获取 `object.cpp`，`string.cpp` 和 `runtime_napi.cpp` 文件的所在目录的路径

```bash
taihec --print-runtime-source-path
```

可以使用命令获取 `taihe/include` 文件夹的路径

```bash
taihec --print-runtime-header-path
```
