# Taihe 异步机制设计文档 (WIP)

## 1. 设计目标与原则

- **高性能**: 异步操作的创建、传递和完成应尽可能减少开销。避免不必要的内存分配和线程切换，尤其是在 C++ 核心层。
- **ABI 稳定性**: 异步模型的底层 ABI 必须是稳定、简洁且与具体语言无关的 C ABI，以确保跨编译器、跨平台的二进制兼容性。
- **易于投影和语言中立**: 核心异步模型应能被轻松地“投影”到各种上层语言（如 C++, ArkTS，仓颉）的原生异步模式中，例如 C++17 的 `std::future`、C++20 的协程、ArkTS 的 `Promise` 和 `AsyncCallback`、仓颉的 `Future` 等等，为开发者提供符合其语言习惯的自然体验。
- **取消支持**: 异步操作应支持取消（Cancellation），允许调用者在不需要结果时提前终止操作。
- **原子化、模块化的 API**: 尤其是在 ABI 层，应提供最基础、可组合的原语。
- **易用性**: 提供强大的组合能力（如 `then`），允许开发者轻松构建复杂的异步工作流，避免“回调地狱”。

## 2. 核心设计思路

### 2.1 模型选择：分离式 Promise/Future

Taihe 异步机制的核心采用了**分离式的 Promise/Future 模型**，将一个异步操作的“生产者”和“消费者”分离为两个独立但关联的对象：

- **`completer` (生产者/Promise)**: 负责在异步操作完成后“设置”结果或错误。它代表了写入端。
- **`future` (消费者/Future)**: 负责注册一个回调（Handler），用于在结果可用时“消费”它。它代表了读取端。

这两个对象通过一个共享的、引用计数的内部状态 `async_context` 关联起来。

### 2.2 设计权衡与对比

- **对比传统回调 (Callbacks)**:
  - 传统回调模式简单直观，但容易导致深度嵌套，形成“回调地狱”，难以管理和维护。

- **对比协程 (Coroutines, async/await)**:
  - 协程为开发者提供了同步风格的异步代码编写体验，是目前最友好的异步方案。
  - 然而，不同语言对协程的支持差异较大，不像 Promise/Future 模型那样有相对统一的接口标准。
  - 协程更像是一种“实现机制的抽象”而非“接口功能的抽象”。它同时覆盖了异步任务和生成器等多种不同的场景，这些场景只是共享了同一套底层实现机制，但目的、功能可能完全不同，且并非所有语言都通过协程来统一它们。在 IDL 层面使用同一套机制描述它们可能带来额外的复杂性。并且，支持协程的语言通常也会针对这些具体场景提供更加专用的功能。例如，C++ 23 和 C++ 26 分别引入了 `std::generator` 和 `std::execution`，它们虽然在底层实现上都依赖 C++ 20 引入的协程机制，但面向不同的使用场景提供了完全不同的接口。
  - 对于不涉及生成器的**异步任务**场景（这也是 IDL 语言需要考虑的最主要场景）而言，协程模型和 Promise/Future 模型本质上是等价的，并且在很多语言的实现中，前者就是后者的语法糖，完全可以在桥接层封装投影。

## 3. 核心组件与数据结构

### 3.1 ABI 层 (`async.abi.h`)

ABI 层定义了异步模型的内存布局和 C 风格接口，是所有语言投影的基础。

```plaintext
+----------------------+                 +----------------------+
|      TCompleter      |                 |       TFuture        |
|       (生产者)       |                 |       (消费者)       |
|----------------------|                 |----------------------|
| - TAsyncContext* ctx |                 | - TAsyncContext* ctx |
+----------------------+                 +----------------------+
            |                                       |
            |                                       |
            +-------------------+-------------------+
                                |
                                v
                    +-----------------------+
                    |     TAsyncContext     |
                    |  (共享状态/引用计数)  |
                    |-----------------------|
                    | - ref_count           |
                    | - flags               |
                    | - handler_storage     |
                    | - handler_func_ptr    |
                    | - cleanup_func_ptr    |
                    | - result_buffer       |
                    +-----------------------+
```

- **`TAsyncContext`**: 异步操作的共享状态核心。
  - `ref_count`: 引用计数，用于管理 `TAsyncContext` 的生命周期。当 `TCompleter` 和 `TFuture` 都被销毁时，该上下文被释放。
  - `flags`: 一个 32 位标志位，通过原子操作来同步状态，如 `ASYNC_CONTEXT_RESULT_SET` (结果已设置), `ASYNC_CONTEXT_HANDLER_SET` (回调已设置), `ASYNC_CONTEXT_CANCELED` (已取消)。这使得结果和回调的设置顺序无关紧要。使用 `__atomic_*` 系列函数确保跨线程的安全地访问和修改。
  - `handler_storage`: `TAsyncHandlerStorage` 联合体，用于存储 Handler 对象。它利用**小缓冲区优化 (SBO)**，对于体积小的 Handler（不大于一个指针大小），可以直接在栈上存储，避免堆分配；对于大的 Handler，则存储一个指向堆内存的指针。
  - `handler_func_ptr`: 函数指针，用于在结果就绪时调用存储的 Handler。
  - `cleanup_func_ptr`: 函数指针，用于在上下文销"销毁时清理 `storage` 中存储的 Handler。
  - `result_buffer`: 用于存储结果对象的原始内存缓冲区。结果对象通过原地构造（placement new）放置在这里。

- **`TCompleter` 和 `TFuture`**:
  - 这两个结构体非常简单，都只包含一个指向 `TAsyncContext` 的指针 `ctx`。它们是操作共享上下文的轻量级句柄。

### 3.2 C++ 投影层 (`async.hpp`)

C++ 投影层将底层的 C ABI 封装成类型安全、易于使用的现代 C++ 接口。

- **`async_context<Result>`**：`TAsyncContext` 的 C++ 模板化封装，实现了类型安全。它负责管理结果的构造 (`emplace_result`) 和 Handler 的设置 (`emplace_handler`, `new_handler`)，并处理原子标志位的同步逻辑。

- **`completer<Result>`**：生产者端，负责在异步操作完成时设置结果。
  - 提供 `complete(Args&&... args)` 方法，用于原地构造结果对象，并触发已注册的 Handler（如果有）。

- **`future<Result>`**：消费者端，负责注册处理结果的回调 Handler。
  - 提供 `on_complete<Handler, Args...>(Args&&... args)` 方法，用于注册一个 Handler，当结果就绪时调用。Handler 可以是任何可调用对象，且其参数可以是结果值或包含结果值的 `completer`。

*注：`completer<Result>` 和 `future<Result>` 都是不可复制但可移动的类型，确保资源的唯一所有权。*

- **`make_contract<Result>()`**:
  - 这是创建异步操作的标准工厂函数。它在堆上创建一个 `async_context`，并返回一个 `std::pair`，包含配对的 `completer` 和 `future`。

- **组合与同步**:
  - `then(...)`：提供了链式调用能力。它接收一个 `future` 和一个处理函数 (Processor)，并返回一个新的 `future`，表示在前一个结果处理完成后产生的新结果。处理函数既可以是同步的也可以是异步的。
  - `wait(...)`：阻塞等待一个 `future` 完成，并返回结果。
  - `race(...)`：等待多个 `future` 中的第一个完成，并返回其结果。
  - 以上函数只是在 C++ 投影层提供的便捷工具函数，其底层实现仅仅是对 `completer` 和 `future` 提供的基本功能的简单封装和组合。ABI 层提供了一套基础但完备的异步原语，允许开发者在更高层次上构建自己的组合逻辑。

## 4. 对外接口与使用流程

### 4.1 API 提供方 (C++ 实现)

API 的提供者（通常是底层原生代码）需要创建一个异步操作，并返回 `future` 给调用者。

```cpp
// 在 IDL 中定义：function doHeavyTask(): async<String>;
// C++ 实现:
#include <taihe/async.hpp>
#include <thread>

// 这是一个返回 future 的函数
taihe::future<taihe::string> doHeavyTask(taihe::string input) {
    // 1. 创建异步对
    auto [completer, future] = taihe::make_contract<taihe::string>();

    // 2. 在新线程中执行耗时操作
    std::thread([completer = std::move(completer), input = std::move(input)]() mutable {
        // 模拟耗时计算
        std::this_thread::sleep_for(std::chrono::seconds(2));
        taihe::string result = "Processed: " + input;

        // 3. 操作完成，设置结果
        completer.complete(std::move(result));
    }).detach();

    // 4. 立即返回 future 对象供上层使用
    return future;
}
```

### 4.2 API 消费方 (C++ 使用)

API 的消费者获取 `future` 对象，并通过 `on_complete` 或 `then` 来处理结果。

```cpp
// 消费方代码
void run() {
    taihe::future<taihe::string> fst = doHeavyTask("my_data");

    // 方式一：直接设置回调处理器
    struct MyHandler {
        void operator()(taihe::string&& result) const {
            // 在这里处理最终结果
            std::cout << "Result received: " << result << std::endl;
        }
    };
    fst.on_complete<MyHandler>();

    // 方式二：使用 then 进行链式调用
    auto snd = taihe::then<int>(std::move(fst), [](taihe::string&& result) {
        std::cout << "Intermediate result: " << result << std::endl;
        // 返回一个新的 future
        return taihe::future<int>::make_ready(result.size());
    });
    
    // snd 可以继续被消费
    int length = taihe::wait(std::move(snd));
}
```

## 5. 语言投影与桥接

Taihe 异步机制能灵活地适配不同语言的异步范式。以 ArkTS 为例，展示如何将 Taihe 的异步模型投影为 ArkTS 的回调和 Promise 模式。

### 5.1 ArkTS 投影：回调模式

- **IDL**: `function onCancelledWithCallback(ms: i64, result: String, completer: Completer<String>): void;`
- **ArkTS 侧**: 用户传入一个标准的 `AsyncCallback<string>` 函数。
- **桥接层实现**:
  1. Native 侧的桥接函数 `onCancelledWithCallback` 接收到 ArkTS 传来的 `ani_fn_object` (函数对象)。
  2. 它调用 `taihe::make_contract` 创建一个 C++ 异步对。
  3. `completer` 被传递给真正的底层 C++ 业务逻辑 `::hello::onCancelledWithCallback`。
  4. `future` 则通过 `on_complete` 注册一个**包装了 `ani_fn_object` 的 C++ Handler** (`cpp_val_set_cpp_handler_t`)。
  5. 当底层业务完成并通过 `completer` 设置结果时，这个 C++ Handler 被触发，它会获取 ANI 环境，将 C++ 结果 (`taihe::string`) 转换为 `ani_string`，最后通过 `env->FunctionalObject_Call` 调用回 ArkTS 的回调函数。

### 5.2 ArkTS 投影：Promise 模式

- **IDL**: `function onCancelledReturnsPromise(ms: i64, result: String): Future<String>;`
- **ArkTS 侧**: 函数直接返回一个 `Promise<string>`，用户可以使用 `.then()` 或 `await`。
- **桥接层实现**:
  1. Native 侧的桥接函数 `onCancelledReturnsPromise` 调用底层 C++ 业务逻辑，获得一个 `taihe::future<taihe::string>`。
  2. 它立即在 ANI 环境中创建一个 `Promise` 和一个 `Resolver` (`env->Promise_New`)，并将 `Promise` 对象返回给 ArkTS。
  3. 它为 C++ 的 `future` 注册一个**包装了 `ani_resolver` 的 C++ Handler** (`ani_result_cpp_handler_t`)。
  4. 当 C++ 结果就绪时，这个 Handler 被触发，它将结果转换为 `ani_string`，然后调用 `env->PromiseResolver_Resolve` 来 fulfill ArkTS 中的 `Promise`。

这两种模式完美展示了 Taihe 的设计哲学：**底层模型统一，上层表现灵活**。

## 6. 如何从 Native 侧“反向调用”ArkTS-DYN 中的函数/方法 (WIP)

### 6.1 背景

Native 代码有时需要调用上层语言（如 ArkTS）实现的函数或方法。这种“反向调用”面临一个关键挑战：

ArkTS-DYN 和传统 JavaScript 采用**单线程事件循环模型**，所有对上层函数的调用都必须在同一个主线程中进行。当 Native 代码运行在其它线程时，它不能直接调用 ArkTS 函数，而必须通过事件机制（如 NAPI 的 `napi_send_event`）将调用请求发送到主线程队列中等待执行。

这种机制带来两个重要影响：

1. **性能开销**：即使调用最简单的同步函数，也需要等待主线程调度执行完毕后才能拿到结果。
2. **死锁风险**：如果 Native 线程阻塞等待结果，而主线程又在等待该 Native 线程，就会造成死锁。

### 6.2 方案

为了从根本上规避阻塞和死锁风险，采用以下核心设计原则：

**所有从 Native 发起的对 ArkTS-DYN 函数的调用，在 IDL 层都必须被建模为异步操作。**

这意味着，即使 ArkTS 端的函数实现是同步的，其在跨语言边界的接口定义也必须是异步的。这确保了 Native 调用方总能立即获得一个代表未来结果的句柄（`future`），而不会发生阻塞。

### 6.3 示例

假如要在 Native 侧暴露一个函数 `invokeCallback`，该函数接受一个由用户在 ArkTS-DYN 中自己实现的接口对象 `IMyCallback`，并调用其上的方法 `userMethod(data: String): String` 来处理数据。

1. **IDL 定义**：在 IDL 中，将 ArkTS 对象上需要被 Native 调用的方法，其返回值统一封装在 `Future<T>` 中。

    ```taihe
    interface IMyCallback {
      // 即使逻辑可能是同步的，在 IDL 中也声明为异步
      function userMethod(data: String): Future<String>;
    }
    
    function invokeCallback(callbackObj: IMyCallback);
    ```

2. **ArkTS 投影**：为了给 ArkTS 开发者提供灵活性，IDL 中的 `Future<T>` 返回值被投影为 `T | Promise<T>` 的联合类型。这允许开发者根据实际情况选择返回一个同步结果 `T`，或是一个异步的 `Promise<T>`。

    ```ts
    interface IMyCallback {
      // 允许同步或异步实现
      userMethod(data: string): string | Promise<string>;
    }
    
    function invokeCallback(callbackObj: IMyCallback): void;
    ```

3. **Native 实现与调用**：在 Native 侧调用 ArkTS 对象上的 `userMethod` 方法，无论其具体实现的返回值类型是 `T` 还是 `Promise<T>`，都会立即返回一个 `taihe::future<taihe::string>`。Native 代码可以通过注册 Handler 来异步地处理最终结果。

    ```cpp
    void invokeCallback(weak::IMyCallback callbackObj) {
        // 1. 无论 userMethod 是同步还是异步实现，在下层都被转换为异步调用
        taihe::future<taihe::string> future = callbackObj->userMethod("data from native");
    
        // 2. 注册处理器，处理结果
        future.on_complete<struct ResultHandler>(callbackObj);
    }
    ```

4. **ArkTS 用户实现**：ArkTS 开发者可以根据需要选择同步或异步地实现 `userMethod` 方法。

    ```ts
    // 用户实现 IMyCallback 接口
    class MyCallbackImpl implements IMyCallback {
      userMethod(data: string): string {
        // 这里是同步处理逻辑
        return "Processed: " + data;
      }
    }
    
    // 或者异步实现
    class MyAsyncCallbackImpl implements IMyCallback {
      async userMethod(data: string): Promise<string> {
        // 这里是异步处理逻辑
        return new Promise((resolve) => {
          setTimeout(() => resolve("Processed: " + data), 1000);
        });
      }
    }
    
    function main() {
      const callback = new MyCallbackImpl();
      invokeCallback("my_data", callback);
    }
    ```

### 6.4 该方案的问题

1. **与现有 SDK 签名的兼容性**

    在上面的例子中，`Future<string>` 在 ArkTS 侧被投影为 `string | Promise<string>`，从而允许用户在实现接口时灵活地选择同步还是异步地返回结果。但是，假如这个方法原本在 SDK 中声明的返回值类型就是 `string` 或者 `Promise<string>` 中确定的一个，那么这会导致自动生成的方法的运行时签名与原本的声明定义不匹配。一种可能的解决方案是引入额外的 IDL 注解来指定期望的返回类型，但是这可能增加用户的学习负担并引入不必要的复杂性。

2. **类型投影依赖于传递方向**

    在 6.3 节的示例中，`Future<String>` 是从 ArkTS 侧传向 Native 侧的（后简称“上传下”），在这种情况下，在 ArkTS 中将其投影为 `string | Promise<string>` 很合理，因为它允许用户灵活地选择同步或异步地返回结果。然而，如果是从 Native 侧传向 ArkTS 侧的（后简称“下传上”），那么 `Future<String>` 在 ArkTS 侧被投影为 `string | Promise<string>` 就不太合适了，因为此时 `Future<T>` 代表的就是一个来自 Native 的异步结果，在 ArkTS 侧它必然表现为一个 `Promise<T>`。

    一种可能的解决方法是，如果 `Future<string>` 出现在“下传上”的位置，则将其投影为 `Promise<string>`；如果出现在“上传下”的位置，则投影为 `string | Promise<string>`。但这会使得投影逻辑变得复杂，此外，通过 IDL 定义并不能确定一个接口到底是“上传下”还是“下传上”的，所以难以确定正确的投影方式。

3. **`void` 类型的处理**

    返回 `void` 的上层函数在 IDL 中应该怎样定义？目前的 Taihe 类型系统并不打算支持 `void` 作为泛型参数，所以不支持 `Future<void>`。一种可能的解决方案是使用 `Future<unit>`，但是它在上层应该被如何投影？

## 7. 和异常处理机制联动 (TODO)
