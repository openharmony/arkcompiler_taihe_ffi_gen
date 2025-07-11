# Hello World：将 C++ 函数绑定到 ArkTS

Taihe 帮你把 C++ 函数绑定到 ArkTS。如果你已经写好了大量的 C++ 代码，只须编写 Taihe 文件描述接口原型，就能将接口暴露给 ArkTS 使用。

让我们用 C++ 函数 `string add(int32_t a, int32_t b)` 举个例子：

## 环境配置

1. 源码用户环境配置

    Ubuntu 用户运行 `./scripts/install-ubuntu-deps` 一键配置环境

    用户也可以手动配置环境，参考[Link](../../docs/DevSetup.md)

2. prebuilts用户环境配置

    prebuilts 用户无需配置环境

## Taihe 命令行使用方法

Taihe 有两种使用模式 taihec 模式 与 tryit 模式

- 1 taihec

    taihec 仅用于生成代码

    需要输入：.taihe 文件
    输出：生成文件

    基本用法
    ```sh
    taihec [taihe_files ...] [options]
    ```

    | 参数          | 简写 | 说明                                                                     |
    | ------------ | ---- | ------------------------------------------------------------------------ |
    | `--output`   | `-O` | 指定生成的目标文件存放目录（默认：`taihe-generated`）                       |
    | `--generate` | `-G` | 指定要启用的后端生成器，如 `abi-header`、`abi-source`、`c-author` 等        |
    | `--build`    | `-B` | 指定构建系统类型，目前支持 `cmake`（生成 CMakeLists.txt）                   |
    | `--codegen`  | `-C` | 额外的代码生成配置项，例如 `sts:keep-name`、`arkts:module-prefix=prefix` 等 |
    | `--version`  |      | 打印版本信息                                                              |
    | `--help`     | `-h` | 帮助信息                                                                  |

    用户基本使用命令

    生成 C++ ANI 相关代码可使用

    ```sh
    taihec [taihe_files ...] -O [genertaed_dir] -G ani-bridge cpp-author
    ```

    ani-bridge 用于生成 ANI 相关桥接代码，cpp-author 用于生成 C++ 实现模板代码

    注：目前需要将 stdlib/taihe.platform.ani.taihe 加入输入文件

    注：目前 IDE 用户需要额外指定 arkts:module-prefix 与 arkts:path-prefix 用于 ANI 签名, 指定 cmake 用于生成 生成文件的 cmake 变量信息

    ```sh
    taihec [taihe_files ...] -O [genertaed_dir] -G ani-bridge cpp-author -C arkts:module-prefix=[module_name] -C arkts:path-prefix=[pkg_name] -B cmake
    ```

    注：源码用户请在 comiler 目前下使用 `python -m taihe.cli.compiler` 代替命令中的 `taihec`

- 2 tryit

    tryit 用于对一个完整样例进行一个简单的自验证

    基本使用方法

    ```sh
    taihe-tryit [mode] [test_dir] [options]
    ```

    tryit 分为多种模式 \[mode\], 介绍 generate、build、test 三种模式

    使用 tryit 的目录结构

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

    生成代码会位于 generated 目录

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

    注：taihe.platform.ani.taihe 文件用于生成对象比较的功能

    - 2.1 generate 模式

        用于生成 arkts 桥接代码

        命令：`taihe-tryit generate --user sts [test_demo path]`

    - 2.2 build 模式

        不生成代码，将已有的代码进行编译，用于生成了代码后，对生成的代码进行修改的场景

        命令：`taihe-tryit build --user sts [test_demo path]`

    - 2.3 test 模式

        生成代码，并编译运行，用于已经写好了 C++ 实现和 main.ets 测试的场景

        命令：`taihe-tryit test --user sts [test_demo path]`

    注：build 模式与 test 模式的可选参数 --optimization, -O[0, 1, 2, 3], 数字越大，优化程度越高

    示例命令：`taihe-tryit test --user sts [test_demo path] -O3`

    注：目前 taihe 生成的 C++ 代码会严格按照 .taihe 声明的风格，而生成的 ets 代码会会严格按照 .taihe 声明然后将首字母改为小写的风格，如果用户希望生成的所有代码都按照 .taihe 声明的风格，可以在 generate 模式或 test 模式使用 `--sts-keep-name`

    示例命令：`taihe-tryit test --user sts [test_demo path] --sts-keep-name`

## 第一步：编写接口原型

在 IDL 目录下，用一行代码描述接口原型。

**File: `idl/hello_world.taihe`**
```js
function add(a: i32, b: i32): String;
```

## 第二步：生成 C++ 代码骨架
执行 Python 模块 taihe，给出下列参数。会将 idl 目录里面的接口原型生成代码到 gen 目录下。同时开启 author, user, ani 代码生成模式。
```
## 注：taihe文件里的函数与C++规范一致，所以函数会在生成的 ets 侧自动转变为小写字母开头函数
## .taihe
## function FooBar(): void;
## 生成的 ets 侧
## function fooBar(): void;
## 如果希望生成的 ets 侧函数与 taihe 文件一致，可以使用 --sts-keep-name
python -m taihe.cli.tryit test -u sts /path/to/hello_world --sts-keep-name

## 如果希望只生成不测试，可以使用
python -m taihe.cli.tryit generate -u sts /path/to/hello_world --sts-keep-name
```

工具自动生成了 C++ 代码的骨架，代码如下：

**File (Generated): `gen/temp/hello_world.impl.cpp`**
```js
// [省略无关代码]
string add(int32_t a, int32_t b) {
    throw std::runtime_error("Function add Not implemented");
}
TH_EXPORT_CPP_API_add(add);
```

## 第三步：填写业务逻辑
将临时目录中的骨架代码复制到 `author/src` 目录下，我们就可以填写逻辑了。

**File: `author/src/hello_world.impl.cpp`**
```c++
string add(int32_t a, int32_t b) {
    std::string sum = std::to_string(a + b);
    return sum;
}
```

在编写 C++ API 逻辑后，让我们简单写 ArkTS 的测试逻辑：

**File: `user/main.ets`**
```typescript
// 导入自动生成的代码
import * as hello_world from "hello_world";
// 加载 C++ 库
loadLibrary("hello_world");

function main() {
    let sum = hello_world.add(1, 2)
    console.log("1 + 2 = " + sum);
}
```

此时此刻，代码目录结构如下：

```
.
├── author
│   └── src
│       └── hello_world.impl.cpp
├── idl
│   └── hello_world.taihe
└── user
    └── main.ets
```

## 第四步：执行测试
本文使用了仓库中的 `compiler/run-test` 脚本，该脚本会自动编译并执行测试：

```sh
../../compiler/run-test . -ani
# ...
1 + 2 = 3
```

## 扩展阅读：绑定原理

Taihe 会生成一系列的 [ANI](https://gitee.com/wangxing-hw/ani_cookbook) 代码。

1. 虚拟机启动时：Taihe 将 C++ 函数注册给虚拟机，让虚拟机“知道” ArkTS 函数所对应的 C++ 代码。
2. ArkTS 代码执行注册的函数时：Taihe 将 ArkTS 传来的参数翻译给 C++，并执行 C++ 函数。
3. 在 C++ 函数执行完毕时：Taihe 将返回值转换成 ArkTS 值，让虚拟机恢复执行 ArkTS 代码。

具体地：

1. Taihe 生成 `ANI_Constructor`，用于注册 Native 模块。虚拟机加载 DSO 时回调 `ANI_Constructor`，从而将 Native 代码绑定到虚拟机内。

**File (Generated): `generated/src/ani_constructor.cpp`**
```c++
#include "hello_world.ani.hpp"

ANI_EXPORT ani_status ANI_Constructor(ani_vm *vm, uint32_t *result) {
    ani_env *env;
    if (ANI_OK != vm->GetEnv(ANI_VERSION_1, &env)) {
        return ANI_ERROR;
    }
    if (ANI_OK != hello_world::ANIRegister(env)) { // 注意看这里！
        std::cerr << "hello_world" << std::endl;
        return ANI_ERROR;
    }
    *result = ANI_VERSION_1;
    return ANI_OK;
}
```

**File (Generated): `generated/src/hello_world.ani.cpp`**
```c++
namespace hello_world {
ani_status ANIRegister(ani_env *env) {
    ani_class ani_env;
    if (ANI_OK != env->FindClass("hello_world.ETSGLOBAL", &ani_env)) {
        return ANI_ERROR;
    }
    ani_native_function methods[] = {
        {"add_inner", nullptr, reinterpret_cast<void*>(hello_world_add_ANIFunc0)},
    };
    // 注册到 ANI 中。
    if (ANI_OK != env->Class_BindNativeMethods(ani_env, methods, sizeof(methods) / sizeof(ani_native_function))) {
        return ANI_ERROR;
    }
    return ANI_OK;
}
}
```

2. 用户的 `main.ets` 执行，调用 Taihe 生成的对外导出函数 `add`。该函数继续调用 `add_inner` 函数（绑定到 C++）。

**File (Generated): `generated/hello_world.ets`**
```typescript
native function add_inner(a: int, b: int): string;
export function add(a: int, b: int): string {
    return add_inner(a, b);
}
```

3. 虚拟机在执行 `add_inner` 时，会自动切换到 `ANI_Constructor` 注册好的 `hello_world_add_ANIFunc0` 实现，代码如下：

**File (Generated): `generated/src/hello_world.ani.cpp`**
```c++
static ani_string hello_world_add_ANIFunc0([[maybe_unused]] ani_env *env, [[maybe_unused]] ani_object object, ani_int a_ani, ani_int b_ani) {
    taihe::set_env(env);
    // 转换 ArkTS 虚拟机的参数到 C++
    int32_t a_cpp = (int32_t)a_ani;
    int32_t b_cpp = (int32_t)b_ani;
    // 执行 C++ 函数
    ::taihe::string cpp_result = ::hello_world::add(a_cpp, b_cpp);
    // 将 C++ 返回值传回 ArkTS 虚拟机
    ani_string ani_result;
    env->String_NewUTF8(cpp_result.c_str(), cpp_result.size(), &ani_result);
    return ani_result;
}
```

4. 执行过程中，Taihe 使用 `::hello_world::add` 访问 C++ 侧定义的函数。

**File: `author/src/hello_world.impl.cpp`**
```C++
// 定义了 "TH_EXPORT_CPP_API_add" 宏
#include "hello_world.impl.hpp"

taihe::string my_add(int32_t a, int32_t b) {
  std::string sum = std::to_string(a + b);
  return sum;
}

// 展开 TH_EXPORT_CPP_API_add。展开后的代码
// 将当前 C++ 文件中的 my_add 绑定为 ::hello_world::add
TH_EXPORT_CPP_API_add(add);
```
