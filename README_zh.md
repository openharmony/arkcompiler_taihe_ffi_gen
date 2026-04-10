# Taihe 跨语言接口生成工具

## 简介

Taihe 是一个多语言系统接口编程模型，为 OpenHarmony 生态提供跨语言接口定义、桥接代码生成的能力。Taihe 作为连接不同编程语言（如 ArkTS、C++、C）的桥梁，通过一个统一的接口定义语言（IDL）和自动化的代码生成流程，简化跨语言开发的复杂性，提高了接口演进的灵活性和开发效率，并实现 API 的发布方与消费方在二进制级别的隔离。

**图1** Taihe 架构图

![Taihe](./docs/public/figures/architecture_diagram.svg)

如图，使用 Taihe 工具时，开发者首先编写 IDL 文件描述跨语言接口，运行 Taihe 编译器生成多种语言之间的桥接代码，然后在生成的框架中填充实现具体的业务逻辑代码，最后通过 Taihe 提供的相关构建模板，结合 Taihe 运行时库编译链接，得到最终的可执行产物（如动态库、字节码等）。

## 主要目录结构


```
arkcompiler/taihe_ffi_gen
├── compiler/              # - IDL 编译器（对应图中浅蓝色部分）
│   ├── Taihe.g4           #     - ANTLR 语法定义
│   └── taihe/             #
│       ├── utils/         #     - 编译器工具库（错误处理、日志、辅助函数等）
│       ├── cli/           #     - 命令行工具入口（taihec、taihe-tryit）
│       ├── driver/        #     - 编译器整体流程驱动
│       ├── parse/         #     - 编译器前端（词法分析、语法分析）
│       ├── semantics/     #     - 编译器核心（中间表示的类型系统、语义分析）
│       └── codegen/       #     - 代码生成后端
│           ├── abi/       #         - C ABI 代码
│           ├── cpp/       #         - C++ 实现模板
│           ├── ani/       #         - ANI 桥接代码 + ArkTS-STA 投影代码
│           └── napi/      #         - NAPI 桥接代码 + ArkTS-DYN 投影代码
├── stdlib/                #     - Taihe 标准库（编译器内置的 IDL 定义文件）
├── runtime/               # - 运行时及构建模板（对应图中浅绿色部分）
│   ├── include/           #     - C ABI 及 C++ 运行时头文件
│   │   └── taihe/         #
│   └── src/               #     - 运行时实现
├── BUILD.gn               #     - GN 构建模板（OpenHarmony 场景）
├── cmake/                 #     - CMake 构建工具（本地开发/测试场景）
├── test/                  # - 测试项目
├── cookbook/              # - 示例项目
└── docs/                  # - 文档
    ├── public/            #     - 面向 Taihe 使用者的文档
    │   ├── spec/          #         - IDL 语言规范
    │   ├── backend-cpp/   #         - C++ 后端文档
    │   ├── backend-ani/   #         - ANI/ArkTS 后端文档
    │   └── backend-napi/  #         - NAPI 后端文档
    └── internal/          #     - 面向 Taihe 开发者的内部文档
        ├── compiler/      #         - 编译器开发文档
        └── runtime/       #         - 运行时开发文档
```

## 约束

**操作系统**：Ubuntu Linux 22.04

**编译器**：Python 3.11

**运行时**：需使用 C++17 标准编译

**配套构建工具**：CMake 3.14+（本地开发/测试）；GN + Ninja（OpenHarmony 场景）

## 编译构建

支持在 Linux 平台编译出适用于 Windows/Linux/macOS 的多平台版本。

OpenHarmony 环境下的编译命令如下：

```sh
./build.sh --product-name rk3568 --build-target build_taihe_wrapper
```

## 使用说明

### 命令行工具

Taihe 提供了以下两个命令行工具：

- **`taihec`**：核心编译器，用于解析 Taihe IDL 文件并生成目标语言代码
- **`taihe-tryit`**：集成测试工具，用于快速创建、生成、编译和运行测试项目

具体使用说明和开发流程请参考 [Taihe 命令行工具文档](/docs/public/CliReference.md)。

### IDL 语言规范

具体请参考 [Taihe IDL 语言规范](docs/public/spec/IdlReference.md)。

### 各后端使用指南

**C++ 后端**

- [C++ 使用指南](docs/public/backend-cpp/CppUsageGuide.md)：Taihe IDL 中定义的接口和数据结构在 C++ 侧的使用说明，包括接口实现、数据类型映射、Taihe C++ 运行时库的使用等内容
- [生成代码说明](docs/public/backend-cpp/CppGeneratedCode.md)：Taihe 编译器为 C++ 后端生成的代码结构和内容说明

**ArkTS/ANI 后端**

- [Taihe ArkTS/ANI 快速入门](docs/public/backend-ani/AniQuickStart.md)：使用 Taihe 定义接口并在 ArkTS-STA 中调用的快速入门教程（以集成测试场景为例）
- [生成代码说明](docs/public/backend-ani/AniGeneratedCode.md)：Taihe 编译器为 ANI/ArkTS 后端生成的桥接代码和 ArkTS 投影代码的结构与内容说明
- [`.d.ts` 文件与 Taihe IDL 间的映射关系](docs/public/backend-ani/DtsToIdlConversion.md)：根据已有的 ArkTS-STA `.d.ts` 文件来编写 Taihe IDL 文件的说明文档，帮助用户理解如何将现有的 ArkTS 接口定义转换为 Taihe IDL 定义
- [ArkTS 通用注解](docs/public/spec/supported-attributes/ArkTSAttributes.md) 和 [ArkTS-STA 特有注解](docs/public/spec/supported-attributes/AniAttributes.md)：ANI/ArkTS 后端支持的 Taihe IDL 注解列表及其说明
- [示例项目和教程](cookbook/quick_ref/README.md)：按照特性分类的 ANI/ArkTS 示例项目和教程

**ArkTS/NAPI 后端**

- [Taihe ArkTS/NAPI 快速入门](docs/public/backend-napi/NapiQuickStart.md)：使用 Taihe 定义接口并在 ArkTS-DYN 中调用的快速入门教程（以集成测试场景为例）
- [使用指南](docs/public/backend-napi/NapiUsageGuide.md)：Taihe IDL 中定义的接口和数据结构在 ArkTS/NAPI 侧的使用说明，包括接口实现、数据类型映射、Taihe NAPI 运行时库的使用等内容
- [ArkTS 通用注解](docs/public/spec/supported-attributes/ArkTSAttributes.md) 和 [ArkTS-DYN 特有注解](docs/public/spec/supported-attributes/NapiAttributes.md)：NAPI/ArkTS 后端支持的 Taihe IDL 注解列表及其说明

## 开发者文档

以下文档面向 Taihe 编译器和运行时的开发者，包含编译器的架构设计、核心算法、数据结构以及 Taihe 定义的 ABI 规范等内容：

**编译器相关**

- [编译器整体设计文档](docs/internal/compiler/Compiler.md)：Taihe 编译器的整体架构设计、模块划分、核心算法和数据结构说明
- [Taihe IR 设计文档](docs/internal/compiler/IRDesign.md)：Taihe 编译器中间表示（IR）的设计说明，包括 IR 的数据结构、构造和访问等
- [注解系统设计文档](docs/internal/compiler/AttributeSystem.md)：Taihe IDL 注解系统的设计说明，包括注解的语法、语义、编译器中的处理流程以及如何在后端代码生成中使用注解信息等内容
- [Taihe 编译器后端开发文档](docs/internal/compiler/BackendAndOptions.md)：编写 Taihe 编译器后端（如 C++、ANI、NAPI）的开发指南，包括后端中的阶段划分、各个阶段的职责和约束、与整体编译流程的交互、编译选项的设计和实现等

**运行时相关**

- [Taihe ABI 文档](docs/internal/runtime/AbiStandard.md)：Taihe 定义的跨语言调用约定和数据类型表示规范
- [Taihe 面向对象/接口系统设计和实现文档](docs/internal/runtime/InterfaceAbi.md)：Taihe 面向对象系统设计和 ABI 规范的详细说明，包括对象模型、内存管理、接口调用约定等内容
- [运行时头文件职责划分说明](docs/internal/runtime/RuntimeHeaders.md)：Taihe 运行时库中头文件的职责划分和内容说明

## 相关仓

[**arkcompiler_taihe_ffi_gen**](https://gitcode.com/openharmony-sig/arkcompiler_taihe_ffi_gen)

[arkcompiler\_runtime\_core](https://gitcode.com/openharmony/arkcompiler_runtime_core)
