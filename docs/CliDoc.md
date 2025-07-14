# Taihe 基本使用文档

## 环境配置

- 源码用户环境配置

  Ubuntu 用户可运行 `scripts/install-ubuntu-deps` 一键配置环境

  用户也可以手动配置环境，参考[Link](DevSetup.md)

- prebuilts 用户环境配置

  prebuilts 用户无需配置环境

## Taihe 命令行使用方法

Taihe 提供了 `taihec` 和 `taihe-tryit` 两个命令行工具，分别用于代码生成和自测试。

### `taihec`

`taihec` 用于仅生成代码。

#### 基本用法：

- 输入：.taihe 文件
- 输出：生成文件

```sh
taihec [taihe_files ...] [options]
```

| 参数         | 简写 | 说明                                                                     |
| ------------ | ---- | ------------------------------------------------------------------------ |
| `--output`   | `-O` | 指定生成的目标文件存放目录（默认：`taihe-generated`）                       |
| `--generate` | `-G` | 指定要启用的后端生成器，如 `abi-header`、`abi-source`、`c-author` 等        |
| `--build`    | `-B` | 指定构建系统类型，目前支持 `cmake`（生成 CMakeLists.txt）                   |
| `--codegen`  | `-C` | 额外的代码生成配置项，例如 `sts:keep-name`、`arkts:module-prefix=prefix` 等 |
| `--version`  |      | 打印版本信息                                                              |
| `--help`     | `-h` | 帮助信息                                                                  |

#### 用户基本使用命令

生成 C++ ANI 相关代码可使用以下命令：
```sh
taihec [taihe_files ...] -O [genertaed_dir] -G ani-bridge cpp-author
```

其中，`ani-bridge` 表示要生成 ANI 相关桥接代码，`cpp-author` 表示要生成 C++ 实现模板代码。

*注：用户可以使用 `path/to/idl/*` 来输出一个idl目录内的所有文件作为 `taihec` 的输入*

*注：目前需要将 `stdlib/taihe.platform.ani.taihe` 也加入输入文件*

*注：IDE 用户需要额外指定 `arkts:module-prefix` 与 `arkts:path-prefix` 用于 ANI 签名, 指定 cmake 用于生成 生成文件的 cmake 变量信息*

```sh
taihec [taihe_files ...] -O [genertaed_dir] -G ani-bridge cpp-author -Carkts:module-prefix=<module_name> -Carkts:path-prefix=<pkg_name> -B cmake
```

*注：源码用户请在 comiler 目录下使用 `python -m taihe.cli.compiler` 代替命令中的 `taihec`*

### `taihe-tryit`

`taihe-tryit` 用于对一个完整样例进行一个简单的自验证

#### 基本用法

```sh
taihe-tryit [mode] [test_dir] [options]
```

`taihe-tryit` 分为多种模式（mode）, 主要介绍 `create`、`generate`、`build`、`test` 几种模式：

- `create`

  用于创建一个新的测试样例目录，包含必要的目录结构和文件，例如：
  ```sh
  taihe-tryit create [test_demo path]
  ```

- `generate`

  用于生成桥接代码，例如：
  ```sh
  taihe-tryit generate --user sts [test_demo path]
  ```

- `build`

  不生成代码，将已有的代码进行编译，用于生成了代码后，对生成的代码进行修改的场景，例如：
  ```
  taihe-tryit build --user sts [test_demo path]
  ```

- `test`

  生成代码，并编译运行，用于已经写好了 C++ 实现和 main.ets 测试的场景，例如：
  ```
  taihe-tryit test --user sts [test_demo path]
  ```

*注：`build` 模式与 `test` 模式的可选参数 `--optimization`, `-O[0,1,2,3]`, 该参数会被传给 C 编译器*

```sh
taihe-tryit test --user sts [test_demo path] -O3
```

*注：目前太和生成的 C++ 代码会严格按照 .taihe 声明的风格，而生成的 ets 代码会会严格按照 .taihe 声明然后将首字母改为小写的风格，如果用户希望生成的所有代码都按照 .taihe 声明的风格，可以在 `generate` 模式或 `test` 模式使用 `--sts-keep-name`*

```sh
taihe-tryit test --user sts [test_demo path] --sts-keep-name
```

#### 使用 tryit 的目录结构

```sh
test_demo/
├── idl/                            # .taihe 文件目录
|   ├── example0.taihe
│   └── example1.taihe
├── author/                         # 用户自己写的实现代码（可选）
|   ├── include/
|        └── author.h
│   └── src/
|        └── author.cpp
|        └── ani_constructor.cpp    # ani 注册文件
└── user/
    └── main.ets                    # 用户测试用 main.ets
```

生成代码会位于 generated 目录：

```sh
generated
├── @ohos.base.ets                   # 用于导入 BusinessError，用户上库不需要
├── hello_world.ets
├── include                          # 生成的 C/C++ 头文件目录
│   ├── hello_world.abi.h
│   ├── hello_world.ani.hpp
│   └── ...
├── src                              # 生成的 C/C++ 源文件目录
│   ├── hello_world.abi.c
│   ├── hello_world.ani.cpp
│   ├── taihe.platform.ani.abi.c
│   └── taihe.platform.ani.ani.cpp
├── taihe.platform.ani.ets           # 无需关注，无需使用
└── temp                             # 用于方便用户使用的模板文件，用户可以复制这些文件到author目录下进行修改
    ├── ani_constructor.cpp
    ├── hello_world.impl.cpp
    └── taihe.platform.ani.impl.cpp  # 无需关注，无需使用
```

*注：`taihe.platform.ani.taihe` 文件用于生成对象比较的功能*
