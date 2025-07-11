# 太和 ANI 用户文档

本文档旨在介绍太和 ANI 后端生成的代码和函数调用链，帮助用户理解如何在自己的代码中使用并调试这些自动生成的接口。

## ⚠ 特别注意 ⚠
***自动生成的 ets 文件中，所有以 `_taihe_` 为前缀的函数和变量，均为太和的内部接口，我们不会保证这些接口的稳定性，因此，请不要勿在用户代码或注入代码中直接调用这些接口！！！***

## 基本函数的正向调用链

假设我们有一个 IDL 文件 `my.package.taihe`，其中定义了两个简单的结构体 `MyParam` 和 `MyResult`，以及一个函数 `process`：
```ts
struct MyParam {
    int a;
    int b;
}

struct MyResult {
    int sum;
}

function process(param: MyParam): MyResult;
```

当在上层代码 `user/main.ets` 中调用该 `process` 函数时，它会经历如下步骤：

1. 进入自动生成的 `generated/my.package.ets` 文件中的 `process` 函数实现。
2. 该 `process` 函数中会进一步调用进同一文件中的 `_taihe_process_native` 函数，该函数与 `generated/src` 目录下的 `my.package.ani.cpp` 文件中的 `local::process` 函数相绑定。
3. `local::process` 函数会先处理参数，将 `MyParam` 在上层对应的 JS 对象（在 ANI 中的类型为 ani_object）转换为 taihe 自动生成的 `my::package::MyParam` 结构体对象，这一转换的具体逻辑通常会实现在 `generated/include/my.package.MyParam.ani.1.hpp` 文件中，对应的转换函数为 `taihe::from_ani<my::package::MyParam>`。
4. 接下来，`local::process` 函数会调用 `my::package::process` 函数，这个函数的调用会被自动转发到接口作者在自己的 C++ 实现文件中，通过 TH_EXPORT_CPP_API_process 这个宏所导出的具体实现。
5. `my::package::process` 函数执行完毕后，拿到 `MyResult` 结构体对象，并将其转换为 ani_object 对象，与第 3 步类似，该转换的具体逻辑会实现在 `generated/include/my.package.MyResult.ani.1.hpp` 文件中的 `taihe::into_ani<my::package::MyResult>` 函数里。
6. 最后，`local::process` 函数的返回值会被传递回上层的 `_taihe_process_native` 函数，进而返回到 `process` 函数，最终返回到用户代码中。

## 反向调用链

反向调用指的是从 C++ Native 代码回调到上层的 JS 代码。例如：
```ts
interface MyCallback {
    onResult(result: MyResult): void;
}

function processWithCallback(param: MyParam, myCallback: MyCallback): void;
```

在这种情况下，回调的过程如下：
1. 首先，当 `myCallback` 对象从上层传入时，它会从 JS 对象被封装成一个太和代理对象。你可以在 `generated/include/my.package.MyCallback.ani.1.hpp` 文件中找到对应的封装过程（如果是 `() => void` 这样的匿名函数，则应在 `generated/src/my.package.ani.cpp` 文件中找到对应的封装过程）。这一封装过程会将太和代理对象上的 `onResult` 方法与 ets 代码中 `interface MyCallback` 内由太和自动生成的 `_taihe_onResult_revert` 方法相绑定。
2. 当 `myCallback->onResult` 被调用时，会进入代理对象的 `onResult` 方法，该方法中会先将回调所需的参数 `MyResult` 结构体对象转换为 ani_object 对象，这一转换过程同正向调用链中的第 5 步。
3. 接下来，代理对象上的 `onResult` 方法会通过 ANI FunctionCall 调用进上层的 `_taihe_onResult_revert` 方法。
4. `_taihe_onResult_revert` 方法会进一步调用上层 JS 对象上的 `onResult` 方法，执行完毕后拿到返回值（如果有），然后回到下层。
5. 在太和代理对象的 `onResult` 方法中再将返回值从 ani_object 转换为对应的 C++ 对象（同正向调用链第 3 步），并返回到 `myCallback->onResult` 的调用处。
