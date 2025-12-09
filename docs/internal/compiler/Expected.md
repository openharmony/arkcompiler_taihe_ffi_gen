# 异常处理系统设计文档

## 1. 异常处理模式分析

### 1.1 C++异常（throw/catch）
**实现方式**：
```cpp
try {
    throw std::runtime_error("error");
} catch (const std::exception& e) {
    // 处理异常
}
```

**优点**：

语法简洁，自动栈展开，资源管理方便，异常类型系统丰富

**缺点**：

性能开销大（栈展开、类型信息），与C ABI不兼容，代码体积膨胀，代码优化限制，编译器必须保守地假设任何函数都可能抛出

### 1.2 返回错误码模式
**实现方式**：

```cpp
int result = function_call();
if (result != SUCCESS) {
    // 处理错误
}
```

**优点**：

零运行时开销，与C完全兼容，确定性执行流程

**缺点**：

错误信息有限，容易忽略错误检查，错误处理代码冗长，难以处理复杂错误情况

### 1.3 长跳转模式（longjmp）
**实现方式**：

```cpp
jmp_buf env;
if (setjmp(env) == 0) {
    // 可能出错的代码
} else {
    // 错误处理
}
```
**优点**：

性能开销低，提供跨函数跳转能力

**缺点**：

资源泄漏风险，可维护性差，与现代C++不兼容，对象不会自动销毁

### 1.4 Expected模式（Sum Type）
**实现方式**：

```cpp
expected<int, Error> result = function_call();
if (!result) {
    // 处理错误
}
```
**优点**：

类型安全，强制错误处理，编译时优化，携带丰富的错误信息

**缺点**：

需要用户显式检查，处理错误，调试复杂性

## 2. Error类型设计分析
### 2.1 多态Error类型
```cpp
class Error {
public:
    virtual ~Error() = default;
    virtual std::string message() const = 0;
};

class NetworkError : public Error { /* ... */ };
class FileError : public Error { /* ... */ };
```
**缺点**：

动态分配开销，类型映射复杂，跨语言边界困难

### 2.2 枚举Error类型
```cpp
enum class ErrorCode {
    Success,
    NetworkError,
    FileNotFound,
    // ...
};

struct Error {
    ErrorCode code;
    std::string message;
};
```
**缺点**：

扩展性受限，错误信息有限

### 2.3 泛型Error类型（Rust风格）
```cpp
template<typename E>
class Error {
    E error;
    std::string message;
};
```
**缺点**：

类型系统复杂，调用方必须处理具体的 error 类型，跨语言映射困难

### 2.4 单一Error类型

error code 的选择有两种，字符串或数字，选择字符串的优点是可读性高，数字的优点是性能更好。
ohos 提供的 BusinessError 内的 code 是数字类型，现有的 SDK 子系统改造开发者在 1.1 和 1.2 里使用的错误码也都是数字类型。
napi 提供的 napi_throw_error 抛出的 error 内的 code 是字符串类型，不确定三方应用倾向于使用哪种类型的错误码，暂定错误码类型为 int。

```cpp
class error {
private:
  int32_t code_;
  ::taihe::string message_;
}
```

**缺点**：

错误信息有限，类型上无法提供信息

## 3. 规格

### 3.1 设计模式选择

**选择 Expected 模式**：

Expected 模式平衡了类型安全和性能，考虑到正确性优先，希望强制用户处理错误，避免遗漏。

没有选择其他模式是考虑到，throw/catch 模式通常搭配 error 类型系统，实现 catch 指定类型的 error，判断会增加复杂度，且结合现有使用情况（ArkTS）来看无需这一功能；错误码模式只能记录 error code，以子系统 SDK 改造用户为例，error message 是常见的需要传递的信息；longjmp 模式会破坏 RAII 模式，容易引发内存泄漏，不安全。

**选择单一 error 模式**：

不同语言的 error 类型系统不统一，难以映射，只提供基本的 error （包含 code 和 message）既保持语言中立，又可以满足用户需求。

没有选择其他模式是考虑到，假如在 IDL 中定义 error 类型系统，一方面在桥接代码中需要判断具体的 error 类型来做映射，增加了复杂度，一方面类型系统的设计需考虑到上下层多种语言，每种语言的类型系统差距较大，难以找到合适的映射；单纯 error code 信息不足；纯用户自定义 error 类型过于自由，难以确定投影到上层的数据结构。

以 ArkTS SDK 子系统改造为例，单一 error 可以满足用户需求。一方面大部分 SDK 接口定义中规定可能抛出的都是 BusinessError（即只包含 code 和 message），另一方面对于少量可能抛出其他类型 Error 的接口，其 Error 内容也只包含 code 和 message，只是类型名字不同。对于少量特殊 Error 的场景，用户都可以上层封装实现。如返回只包含 code 和 message 但名字不为 Error/BusinessError 的情况，在上层在封装一个函数，先 catch Error/BusinessError，然后再 throw new xxxError()；如 error 中包含 data，用户同样可在上层封装函数，分别调用下层返回 error 和 data 的两个函数，再组装并抛出。

另外调研过程中发现用户代码中存在使用 Opaque 表示 BusinessError 的场景，具体分析发现其全部是为了表示 Asynccallback，所以支持下层异步后这部分 Opaque 自然可被取消，暂无需求 BusinessError 类型有确切 IDL 语法表示的场景。

另外 Taihe error 的数据结构设计考虑不同语言的 error 类型结构不一，在 ArkTs 里 error 只有 string 类型的 message，在 ArkTs 1.1 里可以给 error 附加 string 类型的 code，在 ArkTs 1.2 里一般使用附加 int 类型 code 的 BusinessError，如何设计 Taihe 的 Error 的数据结构有待考量，备选方法之一是考虑使用序列化的设计思路，将 code 转为 string 自动拼接到 message 上。

### 3.2 使用规格

- expected 和 error 在 IDL 中无需表示，不能做参数，IDL 中定义函数返回值类型为 `ResultT` 在没有使用其他注解的情况下默认被视为返回值类型为 `::taihe::expected<ResultT, ::taihe::error>` ，error 只能作为 expected 的成员，不能独立使用。

  （出于安全的角度考虑我们默认所有的函数都可能抛出异常，强制用户必须进行错误处理）
- 提供 `@noexcept` 注解（在语法上是一种函数声明注解），标记函数/方法为不可能抛出异常，满足性能敏感接口要求。 
- 只有 `::taihe::error` 一种 error，提供通过 message 和通过 message 和 code 两种方式构造。

expected 只是用于实现 taihe 的异常处理机制，独立于现有类型系统之外，不建议用户独立使用

## 4. 具体实施
### 4.1 核心类型定义

```cpp
class error {
private:
  int32_t code_;
  ::taihe::string message_;
}

// ========== 非 void 主模板版本 ==========
template<typename T, typename E>
class expected {
public:
  using value_type = T;
  using error_type = E;
  ...
private:
  bool has_val;
  union {
    T val;
    E unex;
  };
};

// ========== void 特化版本 ==========
template<typename E>
class expected<void, E> {
public:
  using value_type = void;
  using error_type = E;
  ...
private:
  bool has_val;
  union {
    E unex;
  };
};
```
expected 数据结构与 C++ 23 定义的 std::expected 数据结构基本保持一致，保障用户的开发体验。

### 4.2 ABI 接口设计
**方案一**：

在 ABI 层以 int32_t 作为返回值，0 标识返回 data，1 标识返回 error，使用出参记录具体的 data 或 error。

```cpp
// 现行实现
// C ABI 出参结构体
// data 为 void 类型
typedef union {
    struct TError error;
} hello_sayHello_f_out;
TH_EXPORT int32_t hello_sayHello_f(hello_sayHello_f_out* _taihe_out);

// data 为非 void 类型
typedef union {
    int32_t data;
    struct TError error;
} hello_sayHello_ii_f1_out;
TH_EXPORT int32_t hello_sayHello_ii_f1(hello_sayHello_ii_f1_out* _taihe_out, int32_t a);
```

**方案二**：

在 ABI 层以类似 ::taihe::union 的方式构造返回值的 C ABI 层数据结构，考虑复用现有的 from_abi 和 into_abi 机制进行类型转换。

```cpp
// 新方案，伪代码，未实现
struct hello_sayHello_ii_f1_ret {
    bool flag;
    union {
        int32_t data;
        struct TError error;
    } hello_sayHello_ii_f1_out;
};

TH_EXPORT hello_sayHello_ii_f1_ret hello_sayHello_ii_f1(int32_t a);
```

### 4.3 C ABI 层与 C++ 投影层之间的转换

在 C ABI 层调用 C++ 函数

**方案一**：

```cpp
// 现行实现
template<typename ValueT, typename OutT, typename Func>
int32_t handle_impl_call(Func &&func, OutT *_taihe_out) {
  using result_type = decltype(func());

  if constexpr (std::is_void_v<result_type>) {
    func();
    return 0;
  } else if constexpr (is_expected_v<result_type>) {
    auto result = func();
    if (result.has_value()) {
      if constexpr (!std::is_void_v<ValueT>) {
        _taihe_out->data =
            ::taihe::into_abi<ValueT>(result.value());
      }
      return 0;
    } else {
      _taihe_out->error = ::taihe::into_abi<::taihe::error>(result.error());
      return 1;
    }
  } else {
    auto result = func();
    _taihe_out->data = ::taihe::into_abi<result_type>(result);
    return 0;
  }
}

#define TH_EXPORT_CPP_API_sayHello_ii(CPP_FUNC_IMPL) \
    int32_t hello_sayHello_ii_f1(hello_sayHello_ii_f1_out* _taihe_out, int32_t a) { \
        return ::taihe::handle_impl_call<int32_t>([&]() { \
            return CPP_FUNC_IMPL(::taihe::from_abi<int32_t>(a)); \
        }, _taihe_out); \
    }
```

**方案二**：

```cpp
// 新方案，伪代码，未实现
template<>
struct as_abi<::taihe::expected<int32_t, ::taihe::error>> {
    using type = struct hello_sayHello_ii_f1_ret;
};
template<>
struct as_abi<::taihe::expected<int32_t, ::taihe::error> const&> {
    using type = struct hello_sayHello_ii_f1_ret const*;
};

template<typename ValueT, typename RerturnT, typename OutT, typename Func>
RerturnT handle_impl_call(Func &&func, OutT *_taihe_out) {
  using result_type = decltype(func());

  if constexpr (std::is_void_v<result_type>) {
    func(); 
    return ::taihe::into_abi<::taihe::expected<void, ::taihe::error>>({})
  } else if constexpr (is_expected_v<result_type>) {
    return ::taihe::into_abi<result_type>(func());
  } else {
    auto result = func();
    return ::taihe::into_abi<::taihe::expected<ValueT, ::taihe::error>>(::taihe::expected<ValueT, ::taihe::error>(::taihe::into_abi<result_type>(result)));
  }
}
```

在 C++ 层调用 C ABI 函数

**方案一**：

```cpp
template<typename ValueT, typename FuncT, typename OutT, typename... Args>
::taihe::expected<ValueT, ::taihe::error> make_expected_from_abi_call(
    FuncT &&member_func, OutT *out, Args &&...args) {
  int32_t res_flag = member_func(out, args...);

  if (res_flag == 0) {
    if constexpr (std::is_void_v<ValueT>) {
      return {};
    } else {
      return ::taihe::from_abi<ValueT>(out->data);
    }
  } else {
    return ::taihe::unexpected<::taihe::error>(
        ::taihe::from_abi<::taihe::error>(out->error));
  }
}

inline ::taihe::expected<int32_t, ::taihe::error> sayHello_ii(int32_t a) {
    hello_sayHello_ii_f1_out _taihe_out;
    return ::taihe::make_expected_from_abi_call<int32_t>(
        hello_sayHello_ii_f1, &_taihe_out, ::taihe::into_abi<int32_t>(a));
}
```

**方案二**：

```cpp
inline ::taihe::expected<int32_t, ::taihe::error> sayHello_ii(int32_t a) {
    return ::taihe::into_abi<::taihe::expected<int32_t, ::taihe::error>>(hello_sayHello_ii_f1(::taihe::from_abi<int32_t>(a)));
}
```
