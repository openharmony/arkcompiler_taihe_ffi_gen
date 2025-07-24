# Hello World：将 C++ 函数绑定到 ArkTS

Taihe 帮你把 C++ 函数绑定到 ArkTS。如果你已经写好了大量的 C++ 代码，只须编写 Taihe IDL 文件描述接口原型，就能将接口暴露给 ArkTS 使用。

让我们用 C++ 函数 `string add(int32_t a, int32_t b)` 举个例子：

## 第一步：编写接口原型

在 IDL 目录下，用一行代码描述接口原型。

**File: `idl/hello_world.taihe`**
```js
function add(a: i32, b: i32): String;
```

## 第二步：生成 C++ 代码骨架

```sh
# 注：Taihe IDL 文件里的函数与 C++ 规范一致，所以函数会在生成的 ets 侧自动转变为小写字母开头函数
# Taihe IDL 文件中的写法：
#   function FooBar(): void;
# 生成的 ets 侧代码
#   function fooBar(): void;
# 如果希望生成的 ets 侧函数与 Taihe IDL 文件一致，可以使用 -Csts:keep-name
taihe-tryit test -u sts path/to/hello_world -Csts:keep-name

## 如果希望只生成不测试，可以使用
taihe-tryit generate -u sts path/to/hello_world -Csts:keep-name
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
