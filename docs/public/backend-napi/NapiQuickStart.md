# Taihe Napi 快速入门

**用户在使用 Taihe 开发 Napi 桥接代码时，请专注参考以下核心文档：**

- [Taihe IDL 语言规范](../spec/IdlReference.md)

- [Taihe C++ 数据结构用法](../backend-cpp/CppUsageGuide.md)

- [Taihe Napi 用户文档](./NapiUsageGuide.md)

*其他文档涉及不同后端，与本开发无关。*

## Taihe 命令行使用方法

Taihe 提供了 `taihec` 命令行工具，用于代码生成。

### `taihec`

`taihec` 仅生成代码。
```sh
taihec [taihe_files ...] [options ...]
```

- 输入：Taihe IDL 文件
- 输出：生成文件

*注：`taihe_files` 可以是一个或多个 Taihe IDL 文件，也可以使用通配符，例如 `path/to/idl/*.taihe` 来指定多个文件。*

#### 命令行选项

| 参数 | 简写 | 说明 |
| ---- | ---- | ---- |
| `--output <path>` | `-O<path>` | 指定生成的目标文件存放目录（默认：`taihe-generated`） |
| `--generate <backend>` | `-G<backend>` | 指定要启用的代码生成后端，如 `abi-header`、`abi-source`、`c-author` 等 |
| `--build <build-system>` | `-B<build-system>` | 指定构建系统类型，目前支持 `cmake`（生成 `CMakeLists.txt`） |
| `--version` | | 打印版本信息 |
| `--help` | `-h` | 帮助信息 |

#### 代码生成后端

代码生成后端决定了 `taihec` 会生成哪些代码文件。后端之间存在依赖关系，工具会自动根据配置的后端来递归地启用所需的其他后端，生成完整的代码。

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
taihec test/napi_string/idl/*.taihe -Otest/napi_string/generated -Gnapi-bridge -Gcpp-author  # 生成用户自己在 IDL 中定义的接口的 NAPI 桥接代码，以及 C++ 实现模板等
```

## 使用流程

下面我们以一个 memberTest 项目为例，展示其标准流程。

1. **准备工具**

   - 获取解压后的 Taihe 工具包
   - 存放路径可自定义（无特殊限制）

2. **编写 Taihe 文件**

   - **命名规则**：
     ```plaintext
     [a-zA-Z_][a-zA-Z0-9_.]*.taihe
     ```
     - 正确示例：`member_test.taihe`
     - 含特殊字符时需使用注解：
       ```rust
       @!namespace("@my.module")
       ```
   - 文件存放目录无限制
   - 内容规范详见[Taihe Napi 用户文档](./NapiUsageGuide.md)

3. **生成桥接代码**
   执行生成命令（参数说明）：

   ```bash
   taihec <输入.taihe文件> -O <输出目录> -G napi-bridge cpp-author
   ```

   - **生成内容**：
     - Napi 桥接代码（C++）
     - `.d.ts` 声明文件（默认同原名，含 `@!namespace` 时按注解命名）
     - `.ts` 代理实现文件，只有用户需要（使用 `@!lib` 注解）时会生成，存储在 `//generated/proxy` 目录下，与 `.d.ts` 声明文件同名

   **实际用例**：

   ```bash
   ./taihe/bin/taihec .memberTest/entry/src/main/idl/member_test.taihe \
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
                       └── member_test.taihe  # 源文件
   ```

4. **书写 .cpp 文件**
   运行 taihec 命令会在 `memberTest/entry/src/main/generated/temp` 目录下生成 cpp 实现文件模板 `membertest_test.impl.cpp`，需要用户将其拷贝到存放实现文件的目录中并手动填写实现逻辑

5. **将生成文件加入编译流程**
   以 IDE 中内置的 CMakeLists.txt 文件为基础，需要进行以下修改：

   - Taihe 生成代码需使用 c++ 17 标准编译，需要在 CMakeLists.txt 文件中新增以下内容
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
     //base_dir/taihe/src/taihe/runtime/napi_runtime.cpp
     )

     target_include_directories(entry
     PUBLIC
     //base_dir/taihe/include
     ../generated/include
     )
     ```

可以使用命令获取 `object.cpp`，`string.cpp` 和 `napi_runtime.cpp` 文件的所在目录的绝对路径

```bash
taihec --print-runtime-source-path
```

可以使用命令获取 `taihe/include` 文件夹的绝对路径

```bash
taihec --print-runtime-header-path
```
