# Taihe: 多语言系统接口编程模型

## Taihe 是什么

Taihe 提供了简单易用的 API 发布和消费机制。

对于 API 发布方，Taihe 可以轻松地描述要发布的接口。
```rust
// idl/integer.arithmetic.taihe

struct DivModResult {
    quo: i32;
    rem: i32;
}

function divmod_i32(a: i32, b: i32): DivModResult;
```

Taihe 在发布方和消费方之间生成跨语言的绑定，提供各种语言的原生开发体验。

- 发布方
  ```cpp
  // 发布 API 为 libinteger.so，源码位于 author/integer.arithmetic.impl.cpp

  #include "integer.arithmetic.impl.hpp"

  integer::arithmetic::DivModResult ohos_int_divmod(int32_t a, int32_t b) {
    return {
        .quo = a / b,
        .rem = a % b,
    };
  }

  TH_EXPORT_CPP_API_divmod_i32(ohos_int_divmod)
  ```

- 消费方
  ```cpp
  // 使用 libinteger.so 编写用户应用

  #include "integer.arithmetic.abi.hpp"
  #include <cstdio>

  using namespace integer;

  int main() {
    auto [quo, rem] = arithmetic::divmod_i32(a, b);
    printf("q=%d r=%d\n", quo, rem);
    return 0;
  }
  ```

Taihe 将 API 的发布方和消费方在二进制级别隔离，允许二者在闭源的情况下独立升级。

## 用户指南

如果想要快速上手并有效使用 Taihe，可以阅读以下文档，涵盖了从环境配置到具体使用的详细内容。

- [Taihe 工具的环境配置及使用](docs/QuickStart.md)
- [Taihe IDL 语言规范](docs/IdlReference.md)
- [Taihe IDL 中支持的注解](docs/SupportedAttributes.md)
- [Taihe C++ 使用文档](docs/CppUsageGuide.md)
- [Interface 的二进制标准](docs/InterfaceAbi.md)
- [深入理解 Taihe C++ 生成代码](docs/CppGeneratedCode.md)
- [深入理解 Taihe ANI 生成代码](docs/AniGeneratedCode.md)

关于 ANI 开发的更多教程可以参考 [Taihe ANI CookBook](cookbook/README.md).

## 开发指南

我们欢迎并鼓励社区开发者参与到 Taihe 的开发中来。如果你有兴趣参与 Taihe 的开发，以下文档可以帮助您深入了解项目的设计与实现，并顺利地开始您的贡献。

- [整体设计](docs/Architecture.md)
- [搭建开发环境](docs/DevSetup.md)
- [Taihe 编译器设计文档](docs/Compiler.md)
- [Taihe 注解系统设计文档](docs/AttributeSystem.md)
