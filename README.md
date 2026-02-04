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

- 快速开始
  - [Taihe 是什么？](docs/public/Overview.md)
  - [命令行工具使用指南](docs/public/CliReference.md)
  - [Taihe IDL 语言规范](docs/public/spec/IdlReference.md)

- 使用 Taihe 进行 C++ 开发
  - [Taihe C++ 使用文档](docs/public/backend-cpp/CppUsageGuide.md)
  - [Taihe C++ 生成代码解析](docs/public/backend-cpp/CppGeneratedCode.md)

- 使用 Taihe 进行 ArkTS 开发
  - [快速开始 Taihe ANI 开发](docs/public/backend-ani/AniQuickStart.md)
  - [Taihe ANI 生成代码解析](docs/public/backend-ani/AniGeneratedCode.md)
  - [Taihe IDL ArkTS 注解全集](docs/public/spec/supported-attributes/ArkTSAttributes.md)
  - [Taihe IDL ANI 注解全集](docs/public/spec/supported-attributes/AniAttributes.md)

关于 ANI 开发的更多教程可以参考 [Taihe ANI CookBook](cookbook/README.md).

## 开发指南

我们欢迎并鼓励社区开发者参与到 Taihe 的开发中来。如果你有兴趣参与 Taihe 的开发，以下文档可以帮助您深入了解项目的设计与实现，并顺利地开始您的贡献。

- [搭建开发环境](docs/internal/DevSetup.md)

- Taihe 编译器
  - [Taihe 编译器设计文档](docs/internal/compiler/Compiler.md)
  - [Taihe IR 设计文档](docs/internal/compiler/IRDesign.md)
  - [Taihe 注解系统设计文档](docs/internal/compiler/AttributeSystem.md)

- Taihe ABI 及运行时
  - [Taihe ABI 标准](docs/internal/runtime/AbiStandard.md)
  - [Taihe Interface ABI 设计文档](docs/internal/runtime/InterfaceAbi.md)
  - [Taihe 版本演进规格](docs/internal/runtime/VersionEvolutionStandard.md)
