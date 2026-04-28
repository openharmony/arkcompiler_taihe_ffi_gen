# Taihe跨语言接口定义与代码生成工具

## 简介

Taihe是一个面向OpenHarmony生态的跨语言接口定义与代码生成工具。Taihe作为连接不同编程语言（如ArkTS、C++、C）的桥梁，通过统一的接口定义语言（IDL，Interface Definition Language）和自动化的代码生成流程，简化跨语言开发的复杂性，提高了接口演进的灵活性和开发效率，并实现API的发布方与消费方在二进制级别的隔离。

**图1** Taihe架构图

![Taihe](./docs/public/figures/architecture_diagram.svg)

如图，Taihe工具由**IDL编译组件**和**项目构建组件**两大组件构成，并依赖外部运行时提供语言桥接能力。使用Taihe工具时，开发者首先编写IDL文件描述跨语言接口，运行Taihe编译器生成多种语言之间的桥接代码，然后在生成的框架中填充实现具体的业务逻辑代码，最后通过Taihe提供的相关构建模板，结合Taihe运行时库编译链接，得到最终的可执行产物（如动态库、字节码等）。

### 组件说明

**IDL编译组件**

Taihe IDL编译器负责将`.taihe`接口描述文件解析并编译为目标语言代码。编译器由三部分组成：

- **编译器前端**：进行词法分析和语法分析，将IDL源文件转换为编译器的中间表示（IR，Intermediate Representation）。
- **编译器核心**：对中间表示进行类型检查、名称解析和语义验证，确保接口定义正确无误。
- **编译器后端**：采用插件化设计，将经过验证的中间表示转换为目标语言代码。每个代码生成后端以插件形式存在，负责独立的代码生成，后端之间通过声明依赖关系自动组合——用户只需指定最终需要的后端，编译器会自动启用其所依赖的全部后端。当前提供以下代码生成后端：
  - **C ABI代码生成后端**：生成与语言无关的C ABI层头文件和源文件，是所有其它语言后端的基础。
  - **C++投影和模板代码生成后端**：在C ABI之上生成C++类型投影、接口提供方实现模板和消费方使用的头文件。
  - **ANI → ArkTS-Sta桥接代码生成后端**：生成[ANI（ArkTS Native Interface）](https://gitcode.com/openharmony/docs/blob/OpenHarmony_feature_20250702/zh-cn/application-dev/ani/ani-usage-scenarios.md)桥接代码和[ArkTS-Sta](https://gitcode.com/openharmony/docs/blob/OpenHarmony_feature_20250702/zh-cn/application-dev/quick-start/arkts-sta-user-guide.md)投影代码，使ArkTS-Sta代码能够调用C++实现。
  - **NAPI → ArkTS-Dyn桥接代码生成后端**：生成[NAPI（Node-API）](https://gitcode.com/openharmony/docs/blob/master/zh-cn/application-dev/napi/napi-introduction.md)桥接代码和[ArkTS-Dyn](https://gitcode.com/openharmony/docs/blob/master/zh-cn/application-dev/arkts-utils/arkts-overview.md)投影代码，使ArkTS-Dyn代码能够调用C++实现。

**项目构建组件**

- **构建模板**：Taihe提供了适配不同构建系统的项目模板，帮助用户将生成的代码无缝集成到现有项目的构建流程中。包括适用于OpenHarmony平台的**GN模板**和适用于本地开发测试的**CMake模板**。
- **运行时**：Taihe运行时库为跨语言调用提供底层支撑，包括实现与语言无关的二进制接口约定的**C ABI运行时**，以及在其之上提供C++风格类型封装（如`string`、`array`、`map`等容器类型）和引用计数内存管理的**C++运行时**。

**外部依赖**

Taihe生成的桥接代码在运行时依赖以下外部组件：

- **arkcompiler_runtime_core**：方舟编译器运行时核心，为ArkTS-Sta提供ANI FFI（Foreign Function Interface）能力，是ANI桥接代码的运行时基础。
- **arkcompiler_ets_runtime**：方舟编译器ETS运行时，为ArkTS-Dyn提供NAPI FFI（Foreign Function Interface）能力，是NAPI桥接代码的运行时基础。

以上各组件的详细设计文档参见[Taihe设计文档](#taihe设计文档)一节。

## 主要目录结构

```text
arkcompiler/taihe_ffi_gen
├── compiler/              # - IDL编译组件
│   ├── Taihe.g4           #     - ANTLR语法定义
│   └── taihe/             #
│       ├── utils/         #     - 编译器工具库（错误处理、日志、辅助函数等）
│       ├── cli/           #     - 命令行工具入口（taihec、taihe-tryit）
│       ├── driver/        #     - 编译器整体流程驱动
│       ├── parse/         #     - 编译器前端（词法分析、语法分析）
│       ├── semantics/     #     - 编译器核心（中间表示的类型系统、语义分析）
│       └── codegen/       #     - 编译器后端（代码生成）
│           ├── abi/       #         - C ABI代码生成后端
│           ├── cpp/       #         - C++投影和模板代码生成后端
│           ├── ani/       #         - ANI → ArkTS-Sta桥接代码生成后端
│           └── napi/      #         - NAPI → ArkTS-Dyn桥接代码生成后端
├── stdlib/                #     - Taihe标准库（编译器内置的IDL定义文件）
├── runtime/               # - 项目构建组件：运行时及构建模板
│   ├── include/           #     - C ABI及C++运行时头文件
│   │   └── taihe/         #
│   └── src/               #     - 运行时实现
├── BUILD.gn               #     - GN构建模板（OpenHarmony场景）
├── cmake/                 #     - CMake构建模板（本地开发/测试场景）
├── test/                  # - 测试工程
├── cookbook/              # - 示例工程
└── docs/                  # - 文档
    ├── public/            #     - 面向Taihe使用者的文档
    │   ├── spec/          #         - IDL语言规范
    │   ├── backend-cpp/   #         - C++开发指南
    │   ├── backend-ani/   #         - ArkTS-Sta/ANI开发指南
    │   └── backend-napi/  #         - ArkTS-Dyn/NAPI开发指南
    └── internal/          #     - Taihe设计文档
        ├── compiler/      #         - 编译器设计文档
        └── runtime/       #         - 运行时设计文档
```

## 约束

**操作系统**：Ubuntu Linux 22.04（版本固定，不推荐升级）。

**编译器**：Python 3.11（版本固定，不推荐升级）。

**运行时**：需使用C++17标准编译（版本固定，不推荐升级）。

**配套构建工具**：CMake 3.18及以上（本地开发/测试）；GN+Ninja（OpenHarmony场景）。

## 编译构建

支持在Linux平台编译出适用于Windows/Linux/macOS的多平台版本。

OpenHarmony环境下的编译命令如下：

```sh
./build.sh --product-name rk3568 --build-target build_taihe_wrapper
```

## 使用说明

### 命令行工具

Taihe提供了以下两个命令行工具：

- **`taihec`**：核心编译器，用于解析Taihe IDL文件并生成目标语言代码。
- **`taihe-tryit`**：集成测试工具，用于快速创建、生成、编译和运行测试工程。

具体使用说明和开发流程请参考[Taihe命令行工具文档](/docs/public/CliReference.md)。

### IDL语言规范

具体请参考[Taihe IDL语言规范](docs/public/spec/IdlReference.md)。

### 目标语言开发指南

Taihe支持将C++实现的接口暴露给不同的目标语言调用。下面按目标语言分类列出了相关文档。如果是初次使用Taihe进行跨语言开发，建议从快速入门教程开始。

**ArkTS-Sta（通过ANI桥接）**

适用于将C++实现暴露给ArkTS静态类型代码调用的场景。

- [快速入门](docs/public/backend-ani/AniQuickStart.md)：使用Taihe定义接口并在ArkTS-Sta中调用的快速入门教程（以集成测试场景为例）。
- [生成代码说明](docs/public/backend-ani/AniGeneratedCode.md)：Taihe编译器为ANI/ArkTS生成的桥接代码和ArkTS投影代码的结构与内容说明。
- [`d.ts`文件与Taihe IDL间的映射关系](docs/public/backend-ani/DtsToIdlConversion.md)：根据已有的ArkTS-Sta `d.ts`文件来编写Taihe IDL文件的说明文档，帮助用户理解如何将现有的ArkTS接口定义转换为Taihe IDL定义。
- [ArkTS通用注解](docs/public/spec/supported-attributes/ArkTSAttributes.md)和[ArkTS-Sta特有注解](docs/public/spec/supported-attributes/AniAttributes.md)：ANI/ArkTS支持的Taihe IDL注解列表及其说明。
- [示例工程和教程](cookbook/quick_ref/README.md)：按照特性分类的ANI/ArkTS示例工程和教程。

**ArkTS-Dyn（通过NAPI桥接）**

适用于将C++实现暴露给ArkTS动态类型代码调用的场景。

- [快速入门](docs/public/backend-napi/NapiQuickStart.md)：使用Taihe定义接口并在ArkTS-Dyn中调用的快速入门教程（以集成测试场景为例）。
- [使用指南](docs/public/backend-napi/NapiUsageGuide.md)：Taihe IDL中定义的接口和数据结构在ArkTS/NAPI侧的使用说明，包括接口实现、数据类型映射、Taihe NAPI运行时库的使用等内容。
- [ArkTS通用注解](docs/public/spec/supported-attributes/ArkTSAttributes.md)和[ArkTS-Dyn特有注解](docs/public/spec/supported-attributes/NapiAttributes.md)：NAPI/ArkTS支持的Taihe IDL注解列表及其说明。

**C++**

适用于C++模块之间通过Taihe进行接口解耦的场景。

- [C++使用指南](docs/public/backend-cpp/CppUsageGuide.md)：Taihe IDL中定义的接口和数据结构在C++侧的使用说明，包括接口实现、数据类型映射、Taihe C++运行时库的使用等内容。
- [生成代码说明](docs/public/backend-cpp/CppGeneratedCode.md)：Taihe编译器为C++生成的代码结构和内容说明。

## Taihe设计文档

以下文档面向Taihe项目的代码贡献者，包含编译器的架构设计、核心算法、数据结构以及Taihe定义的ABI规范等内容：

**编译器相关**

- [编译器整体设计文档](docs/internal/compiler/Compiler.md)：Taihe编译器的整体架构设计、模块划分、核心算法和数据结构说明。
- [Taihe IR设计文档](docs/internal/compiler/IRDesign.md)：Taihe编译器中间表示的设计说明，包括数据结构、构造和访问等。
- [注解系统设计文档](docs/internal/compiler/AttributeSystem.md)：Taihe IDL注解系统的设计说明，包括注解的语法、语义、编译器中的处理流程以及如何在后端代码生成中使用注解信息等内容。
- [Taihe编译器后端开发文档](docs/internal/compiler/BackendAndOptions.md)：编写Taihe编译器后端（如C++、ANI、NAPI）的开发指南，包括后端中的阶段划分、各个阶段的职责和约束、与整体编译流程的交互、编译选项的设计和实现等。

**运行时相关**

- [Taihe ABI文档](docs/internal/runtime/AbiStandard.md)：Taihe定义的跨语言调用约定和数据类型表示规范。
- [Taihe面向对象/接口系统设计和实现文档](docs/internal/runtime/InterfaceAbi.md)：Taihe面向对象系统设计和ABI规范的详细说明，包括对象模型、内存管理、接口调用约定等内容。
- [运行时头文件职责划分说明](docs/internal/runtime/RuntimeHeaders.md)：Taihe运行时库中头文件的职责划分和内容说明。

## 相关仓

[**arkcompiler_taihe_ffi_gen**](https://gitcode.com/openharmony-sig/arkcompiler_taihe_ffi_gen)

[arkcompiler_runtime_core](https://gitcode.com/openharmony/arkcompiler_runtime_core)

[arkcompiler_ets_runtime](https://gitcode.com/openharmony/arkcompiler_ets_runtime)
