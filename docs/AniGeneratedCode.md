# 深入解析 Taihe 生成的代码（ANI 桥接层）

本文档旨在介绍 Taihe ANI 后端生成的代码和函数调用链，帮助用户理解如何在自己的代码中使用并调试这些自动生成的接口。

## ⚠️ 特别注意 ⚠️

***自动生成的 ets 文件中，所有以 `_taihe_` 为前缀的函数和变量，均为 Taihe 的内部接口，我们不会保证这些接口的稳定性，因此，请不要在用户代码或注入代码中直接调用这些接口！！！***

## 生成代码的目录结构解析

以下面的 Taihe IDL 文件为例，来说明生成代码的目录结构和文件内容。
```rust
// File: example/idl/my.package.taihe
struct Data {
    a: i32;
    b: String;
}
union Result {
    ok: i32;
    err: String;
}
interface IFoo {
    init(): void;
}
interface IBar: IFoo {
    process(data: Data): Result;
}
function processWithBar(bar: IBar, data: Data): Result;
```

生成的代码目录结构如下：
```
test/xxx/generated/
├── include
│   ├── my.package.*.abi.{0,1,2}.h
│   ├── my.package.abi.h
│   ├── my.package.*.proj.{0,1,2}.hpp
│   ├── my.package.proj.hpp
│   ├── my.package.impl.hpp
│   ├── my.package.user.hpp
│   ├── my.package.*.ani.{0,1}.hpp
│   └── my.package.ani.hpp
├── src
│   ├── my.package.abi.c
│   └── my.package.ani.cpp
├── my.package.ets
└── temp
    ├── ani_constructor.cpp
    └── my.package.impl.cpp
```

其中，`*.abi.h`, `*.proj.h`, `*.user.hpp`, `*.impl.hpp` 的说明可参考 [Taihe ABI 层及 C++ 层生成代码解析](./CppGeneratedCode.md)。

ANI 生成的相关文件说明如下：
- `include/my.package.*.ani.{0,1}.hpp`：包含了所有 `my.package.taihe` 中定义的结构体、枚举、接口等数据类型在 C++ 和 ANI 间相互转换的函数。`*.ani.0.hpp` 包含转换函数的前向声明，`*.ani.1.hpp` 包含这些函数的具体实现。
- `include/my.package.ani.hpp`：包含了 `my::package::ANI_Register` 函数的声明，该函数用于将 `my.package.taihe` 中定义的所有函数注册到 ANI 虚拟机中。
- `src/my.package.ani.cpp`：包含了所有 `my.package.taihe` 中定义的函数的 native 侧桥接代码，以及 `my::package::ANI_Register` 函数的实现。
- `my.package.ets`：包含了所有 `my.package.taihe` 中定义的数据类型和函数的 ArkTS 侧桥接代码。
- `temp/ani_constructor.cpp`：`ANI_Constructor` 函数的实现模板代码，其中调用了 `ANI_Register` 函数，将所有函数的 native 侧实现注册到 ANI 虚拟机中。

## 基本函数的正向调用链

假设我们有一个 Taihe IDL 文件 `my.package.taihe`，其中定义了两个简单的结构体 `MyParam` 和 `MyResult`，以及一个函数 `process`：
```rust
struct MyParam {
    a: i32;
    b: i32;
}

struct MyResult {
    sum: i32;
}

function process(param: MyParam): MyResult;
```

当在上层代码 `user/main.ets` 中调用该 `process` 函数时，它会经历如下步骤：

1. 进入自动生成的 `generated/my.package.ets` 文件中的 `process` 函数实现。

    **generated/my.package.ets**
    ```typescript
    export function process(param: _taihe_my_package.MyParam): _taihe_my_package.MyResult {
        return _taihe_process_native(param);
    }
    ```

2. 该 `process` 函数中会进一步调用进同一文件中的 `_taihe_process_native` 函数，它与 `generated/src` 目录下的 `my.package.ani.cpp` 文件中的 `local::process` 函数相绑定。

    **generated/my.package.ets**
    ```typescript
    native function _taihe_process_native(param: _taihe_my_package.MyParam): _taihe_my_package.MyResult;
    ```

3. `local::process` 函数会先处理参数，将 `MyParam` 在上层对应的 JS 对象（在 ANI 中的类型为 ani_object）转换为 taihe 自动生成的 `my::package::MyParam` 结构体对象，这一转换的具体逻辑通常会实现在 `generated/include/my.package.MyParam.ani.1.hpp` 文件中，对应的转换函数为 `taihe::from_ani<my::package::MyParam>`。

    **generated/src/my.package.ani.cpp**
    ```cpp
    namespace local {
    static ani_object process([[maybe_unused]] ani_env *env, ani_object ani_arg_param) {
        ::my::package::MyParam cpp_arg_param = ::taihe::from_ani<::my::package::MyParam>(env, ani_arg_param); // here
        ::my::package::MyResult cpp_result = ::my::package::process(cpp_arg_param);
        if (::taihe::has_error()) { return ani_object{}; }
        ani_object ani_result = ::taihe::into_ani<::my::package::MyResult>(env, cpp_result);
        return ani_result;
    }
    }
    ```

    **generated/include/my.package.MyParam.ani.1.hpp**
    ```cpp
    inline ::my::package::MyParam taihe::from_ani_t<::my::package::MyParam>::operator()(ani_env* env, ani_object ani_obj) const {
        ani_int ani_field_a;
        env->Object_CallMethod_Int(ani_obj, TH_ANI_FIND_CLASS_METHOD(env, "my.package.MyParam", "<get>a", nullptr), reinterpret_cast<ani_int*>(&ani_field_a));
        int32_t cpp_field_a = (int32_t)ani_field_a;
        ani_int ani_field_b;
        env->Object_CallMethod_Int(ani_obj, TH_ANI_FIND_CLASS_METHOD(env, "my.package.MyParam", "<get>b", nullptr), reinterpret_cast<ani_int*>(&ani_field_b));
        int32_t cpp_field_b = (int32_t)ani_field_b;
        return ::my::package::MyParam{std::move(cpp_field_a), std::move(cpp_field_b)};
    }
    ```

4. 接下来，`local::process` 函数会调用 `my::package::process` 函数，该调用会自动转发到接口作者在 C++ 实现文件中通过 `TH_EXPORT_CPP_API_process` 宏导出的具体实现。

    **generated/src/my.package.ani.cpp**
    ```cpp
    namespace local {
    static ani_object process([[maybe_unused]] ani_env *env, ani_object ani_arg_param) {
        ::my::package::MyParam cpp_arg_param = ::taihe::from_ani<::my::package::MyParam>(env, ani_arg_param);
        ::my::package::MyResult cpp_result = ::my::package::process(cpp_arg_param); // here
        if (::taihe::has_error()) { return ani_object{}; }
        ani_object ani_result = ::taihe::into_ani<::my::package::MyResult>(env, cpp_result);
        return ani_result;
    }
    }
    ```

5. `my::package::process` 函数执行完毕后，拿到 `MyResult` 结构体对象，并将其转换为 ani_object 对象，与第 3 步类似，该转换的具体逻辑会实现在 `generated/include/my.package.MyResult.ani.1.hpp` 文件中的 `taihe::into_ani<my::package::MyResult>` 函数里。

    **generated/src/my.package.ani.cpp**
    ```cpp
    static ani_object process([[maybe_unused]] ani_env *env, ani_object ani_arg_param) {
        ::my::package::MyParam cpp_arg_param = ::taihe::from_ani<::my::package::MyParam>(env, ani_arg_param);
        ::my::package::MyResult cpp_result = ::my::package::process(cpp_arg_param);
        if (::taihe::has_error()) { return ani_object{}; }
        ani_object ani_result = ::taihe::into_ani<::my::package::MyResult>(env, cpp_result); // here
        return ani_result;
    }
    ```

    **generated/include/my.package.MyResult.ani.1.hpp**
    ```cpp
    inline ani_object taihe::into_ani_t<::my::package::MyResult>::operator()(ani_env* env, ::my::package::MyResult cpp_obj) const {
        ani_int ani_field_sum = (int32_t)cpp_obj.sum;
        ani_object ani_obj;
        env->Object_New(TH_ANI_FIND_CLASS(env, "my.package._taihe_MyResult_inner"), TH_ANI_FIND_CLASS_METHOD(env, "my.package._taihe_MyResult_inner", "<ctor>", nullptr), &ani_obj, ani_field_sum);
        return ani_obj;
    }
    ```

6. 最后，`local::process` 函数的返回值会被传递回上层的 `_taihe_process_native` 函数，进而返回到 `process` 函数，最终返回到用户代码中。

## 反向调用链

反向调用指的是从 C++ Native 代码回调到上层的 JS 代码。例如：
```rust
interface MyCallback {
    onResult(result: MyParam): MyResult;
}

function processWithCallback(myCallback: MyCallback): void;
```

在这种情况下，回调的过程如下：
1. 首先，当 `myCallback` 对象从上层传入时，它会从 JS 对象被封装成一个 Taihe 代理对象。你可以在 `generated/include/my.package.MyCallback.ani.1.hpp` 文件中的函数 `taihe::from_ani<test::MyCallback>` 里找到对应的封装/转换逻辑（如果是 `() => void` 这样的匿名函数，则应在 `generated/src/my.package.ani.cpp` 文件中找到对应的转换逻辑）。这一封装过程会将 Taihe 代理对象上的 `onResult` 方法与 ets 代码中 `interface MyCallback` 内由 Taihe 自动生成的 `_taihe_onResult_revert` 方法相绑定。

    **generated/src/my.package.MyCallback.ani.1.hpp**
    ```cpp
    inline ::my::package::MyCallback taihe::from_ani_t<::my::package::MyCallback>::operator()(ani_env* env, ani_object ani_obj) const {
        struct cpp_impl_t : ::taihe::dref_guard {
            cpp_impl_t(ani_env* env, ani_ref val) : ::taihe::dref_guard(env, val) {}
            ::my::package::MyResult onResult(::my::package::MyParam const& cpp_arg_result) {
                ::taihe::env_guard guard;
                ani_env *env = guard.get_env();
                ani_object ani_arg_result = ::taihe::into_ani<::my::package::MyParam>(env, cpp_arg_result);
                ani_object ani_result;
                env->Object_CallMethod_Ref(static_cast<ani_object>(this->ref), TH_ANI_FIND_CLASS_METHOD(env, "my.package.MyCallback", "_taihe_onResult_revert", nullptr), reinterpret_cast<ani_ref*>(&ani_result), ani_arg_result);
                ::my::package::MyResult cpp_result = ::taihe::from_ani<::my::package::MyResult>(env, ani_result);
                return cpp_result;
            }
            uintptr_t getGlobalReference() const {
                return reinterpret_cast<uintptr_t>(this->ref);
            }
        };
        return ::taihe::make_holder<cpp_impl_t, ::my::package::MyCallback, ::taihe::platform::ani::AniObject>(env, ani_obj);
    }
    ```

2. 当 `myCallback->onResult` 被调用时，会进入代理对象的 `onResult` 方法，该方法中会先将回调所需的参数 `MyParam` 结构体对象转换为 ani_object 对象，这一转换过程和正向调用链中的第 5 步类似。

    **generated/src/my.package.MyCallback.ani.1.hpp**
    ```cpp
    inline ::my::package::MyCallback taihe::from_ani_t<::my::package::MyCallback>::operator()(ani_env* env, ani_object ani_obj) const {
        struct cpp_impl_t : ::taihe::dref_guard {
            cpp_impl_t(ani_env* env, ani_ref val) : ::taihe::dref_guard(env, val) {}
            ::my::package::MyResult onResult(::my::package::MyParam const& cpp_arg_result) {
                ::taihe::env_guard guard;
                ani_env *env = guard.get_env();
                ani_object ani_arg_result = ::taihe::into_ani<::my::package::MyParam>(env, cpp_arg_result); // here
                ani_object ani_result;
                env->Object_CallMethod_Ref(static_cast<ani_object>(this->ref), TH_ANI_FIND_CLASS_METHOD(env, "my.package.MyCallback", "_taihe_onResult_revert", nullptr), reinterpret_cast<ani_ref*>(&ani_result), ani_arg_result);
                ::my::package::MyResult cpp_result = ::taihe::from_ani<::my::package::MyResult>(env, ani_result);
                return cpp_result;
            }
            uintptr_t getGlobalReference() const {
                return reinterpret_cast<uintptr_t>(this->ref);
            }
        };
        return ::taihe::make_holder<cpp_impl_t, ::my::package::MyCallback, ::taihe::platform::ani::AniObject>(env, ani_obj);
    }
    ```

    **generated/include/my.package.MyParam.ani.1.hpp**
    ```cpp
    inline ani_object taihe::into_ani_t<::my::package::MyParam>::operator()(ani_env* env, ::my::package::MyParam cpp_obj) const {
        ani_int ani_field_a = (int32_t)cpp_obj.a;
        ani_int ani_field_b = (int32_t)cpp_obj.b;
        ani_object ani_obj;
        env->Object_New(TH_ANI_FIND_CLASS(env, "my.package._taihe_MyParam_inner"), TH_ANI_FIND_CLASS_METHOD(env, "my.package._taihe_MyParam_inner", "<ctor>", nullptr), &ani_obj, ani_field_a, ani_field_b);
        return ani_obj;
    }
    ```

3. 接下来，代理对象上的 `onResult` 方法会通过 ANI FunctionCall 调用进上层的 `_taihe_onResult_revert` 方法。

    **generated/src/my.package.MyCallback.ani.1.hpp**
    ```cpp
    inline ::my::package::MyCallback taihe::from_ani_t<::my::package::MyCallback>::operator()(ani_env* env, ani_object ani_obj) const {
        struct cpp_impl_t : ::taihe::dref_guard {
            cpp_impl_t(ani_env* env, ani_ref val) : ::taihe::dref_guard(env, val) {}
            ::my::package::MyResult onResult(::my::package::MyParam const& cpp_arg_result) {
                ::taihe::env_guard guard;
                ani_env *env = guard.get_env();
                ani_object ani_arg_result = ::taihe::into_ani<::my::package::MyParam>(env, cpp_arg_result);
                ani_object ani_result;
                env->Object_CallMethod_Ref(static_cast<ani_object>(this->ref), TH_ANI_FIND_CLASS_METHOD(env, "my.package.MyCallback", "_taihe_onResult_revert", nullptr), reinterpret_cast<ani_ref*>(&ani_result), ani_arg_result); // here
                ::my::package::MyResult cpp_result = ::taihe::from_ani<::my::package::MyResult>(env, ani_result);
                return cpp_result;
            }
            uintptr_t getGlobalReference() const {
                return reinterpret_cast<uintptr_t>(this->ref);
            }
        };
        return ::taihe::make_holder<cpp_impl_t, ::my::package::MyCallback, ::taihe::platform::ani::AniObject>(env, ani_obj);
    }
    ```

4. `_taihe_onResult_revert` 方法会进一步调用上层 JS 对象上的 `onResult` 方法，执行完毕后拿到返回值（如果有），然后回到下层。

    **generated/my.package.ets**
    ```typescript
    export interface MyCallback {
        onResult(result: _taihe_my_package.MyParam): _taihe_my_package.MyResult;

        _taihe_onResult_revert(result: _taihe_my_package.MyParam): _taihe_my_package.MyResult {
            return this.onResult(result);
        }
    }
    ```

5. 在 Taihe 代理对象的 `onResult` 方法中再将返回值从 ani_object 转换为对应的 C++ 对象（类似正向调用链第 3 步），并返回到 `myCallback->onResult` 的调用处。

    **generated/src/my.package.MyCallback.ani.1.hpp**
    ```cpp
    inline ::my::package::MyCallback taihe::from_ani_t<::my::package::MyCallback>::operator()(ani_env* env, ani_object ani_obj) const {
        struct cpp_impl_t : ::taihe::dref_guard {
            cpp_impl_t(ani_env* env, ani_ref val) : ::taihe::dref_guard(env, val) {}
            ::my::package::MyResult onResult(::my::package::MyParam const& cpp_arg_result) {
                ::taihe::env_guard guard;
                ani_env *env = guard.get_env();
                ani_object ani_arg_result = ::taihe::into_ani<::my::package::MyParam>(env, cpp_arg_result);
                ani_object ani_result;
                env->Object_CallMethod_Ref(static_cast<ani_object>(this->ref), TH_ANI_FIND_CLASS_METHOD(env, "my.package.MyCallback", "_taihe_onResult_revert", nullptr), reinterpret_cast<ani_ref*>(&ani_result), ani_arg_result);
                ::my::package::MyResult cpp_result = ::taihe::from_ani<::my::package::MyResult>(env, ani_result); // here
                return cpp_result;
            }
            uintptr_t getGlobalReference() const {
                return reinterpret_cast<uintptr_t>(this->ref);
            }
        };
        return ::taihe::make_holder<cpp_impl_t, ::my::package::MyCallback, ::taihe::platform::ani::AniObject>(env, ani_obj);
    }
    ```

    **generated/include/my.package.MyResult.ani.1.hpp**
    ```cpp
    inline ::my::package::MyResult taihe::from_ani_t<::my::package::MyResult>::operator()(ani_env* env, ani_object ani_obj) const {
        ani_int ani_field_sum;
        env->Object_CallMethod_Int(ani_obj, TH_ANI_FIND_CLASS_METHOD(env, "my.package.MyResult", "<get>sum", nullptr), reinterpret_cast<ani_int*>(&ani_field_sum));
        int32_t cpp_field_sum = (int32_t)ani_field_sum;
        return ::my::package::MyResult{std::move(cpp_field_sum)};
    }
    ```
