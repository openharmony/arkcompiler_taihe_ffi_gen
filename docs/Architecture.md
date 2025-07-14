# 整体设计

不论是读写文件，还是获取 GPS 定位，App 都需要依赖 OS 提供的 API，才能调用各类软硬件能力。Taihe 是为 OS 设计的 API 编程模型，连接了外部应用的 API 消费者和 OS 的内部能力。

具体地，OS 开发者编写接口合约描述文件后，Taihe 会自动生成 OS 侧的接口层代码，以及各语言的桥接代码，从而让各语言都能方便高效地调用 OS 内部能力。

## 目标和非目标

Taihe 的目标包括：

- **高性能**：基于原生代码，提供类 C 的性能，避免托管代码的虚拟机执行和对象转换开销。
- **易开发**：精选少量的核心语言特性，辅助代码生成，让各类语言的开发者都可以获得类原生语言的开发体验。
- **可演进**：设计稳定的 ABI 保证 OS/App 二进制解耦。OS 组件升级时，现有 App 无需重编译。

在当前阶段，Taihe 存在下列约束：

- **不考虑现有 API 接口的兼容替代**。现有的 C API、NodeJS API 等接口未能完全和实现解耦，接口内包含大量逻辑，导致兼容这些接口需要大量的工作。
- **不支持各类编程语言互相调用**，只支持上层应用的各种编程语言调用底座的 C/C++ 实现。这样的约束让我们只考虑将 C++ 实现向外暴露的场景，用有限的资源支持最重要的工作。
- **不支持直接转换现有的 C++ 实现**。现有的 C++ 代码未能良好分离接口和实现，全自动转换会暴露不必要的内部实现，增加后期维护的成本。

## 系统上下文

Taihe 通过一套二进制接口标准（ABI），连接了 API 的作者和消费者。

### 运行态

在运行态，以 C++ 为例：

1. **程序（消费侧）**，业务逻辑：调用 Taihe 提供的 C++ API。
2. **程序（消费侧）**，*Taihe 转换*：将 C++ API 转换为 Taihe ABI，从而跨越程序和库之间的二进制边界。
3. **库（作者侧）**，*Taihe 转发*：从 Taihe ABI 转发至 C++ 内部实现。
4. **库（作者侧）**，内部实现：按照 Taihe C++ 接口标准，实现 API 背后的逻辑。

### 开发态

由于底层的 ABI 标准不适合业务逻辑的开发，Taihe 自动生成转换和转发的代码。

以使用 C++ 封装传感器能力为例：

1. **`sensors.taihe`**: 权威描述
   - OS 侧编写，说明对外暴露的能力，包括数据结构和函数。
   - 此描述是接口的权威描述，生成的代码、人工编写的代码均需要和此描述保持一致。
2. **`sensors.abi.h`**: ABI 标准
   - 自动生成的 C 头文件，包含函数声明、结构体、枚举值。
   - 此文件是接口的 ABI 描述，基于 C 语言标准，描述对象的内存布局、调用约定、符号名称等信息。
   - 此文件既可用于 C 和 C++，也可用于其他语言的 FFI 工具链。
3. **`sensors.impl.{h,cpp}`**: ABI 转发至作者侧实现
   - 自动生成的 C++ 头文件，方便作者侧将现有 C++ 代码对接到 Taihe ABI。
   - 头文件提供了模板类；现有的 C++ 类以继承的方式，可以自动对接 Taihe 接口。
4. **`sensors.user.{h,hpp}`**: 消费侧 API 调用转换至 ABI
   - 自动生成的 C++ 头文件，提供舒适的 C++ API 供业务逻辑使用 Taihe ABI。

## 编译器

### 基础概念

Taihe 遵从经典的“三阶段”编译器设计，具体地：

1. **前端 (Frontend)**：源代码（文本） → 中间表示（IR）。
   - 例如，字符串 `"function foo();"` 经过词法分析、语法分析后，从一棵抽象语法树转换成了数据结构“全局函数声明” (`GlobFuncDecl`)。
   - 在 Taihe 代码仓内，该部分由 `taihe.parse` 部分完成。
2. **语义分析 (Semantics)**：IR → IR。部分分析结果被附加于 IR 上，同时进行检查。
   - 例如，程序 `function foo(x: BadType, y: GoodType);` 引入了不存在的类型 `BadType`，语义分析在此向用户报告错误。
   - 在 Taihe 代码仓内，该部分由 `taihe.semantics` 部分完成。
3. **代码生成 (Code Generation)**：IR → 源代码。
   - 在 Taihe 代码仓内，该部分由 `taihe.codegen` 部分完成。
   - 由于不同的目标语言有不同的源码规格，Taihe 抽象出“语言后端”的概念，实现目标语言间的解耦。
   - 例如 `taihe.codegen.abi` 用于生成 C 风格的 ABI 接口，而 `taihe.codegen.cpp` 用于生成舒适的 C++ 代码投影。

### 整体流程

`taihe.cli` 负责解析命令行参数，并按需去调用编译器驱动的 Python 接口。这是因为 Taihe 编译器由一个个小小的库组成。这些库只能被 Python 代码所调用，需要封装出对外的命令行接口。

`taihe.driver` 是统筹整个流水线的编译驱动。这是因为编译流程往往包含多个小的环节，实际使用中需要保证先后顺序。例如，生成代码的前提是进行语义分析，否则编译器不知道 `function foo(x: Bar)` 中 `Bar` 的名字背后指什么类型。

让我们串起来整个编译流程。在执行 Python 脚本时，`taihe.cli.compiler` 的 `main` 函数获得执行：

1. 解析命令行参数
2. 初始化 `taihe.driver.backend.BackendRegistry`，创造对应的语言后端。`BackendRegistry` 是语言后端的工厂，帮助从命令行逐步构建语言后端实例。
3. 构造 `taihe.driver.contexts.CompilerInvocation` 实例，描述编译意图。例如，使用 `ani-bridge` 语言后端去编译 `foo.taihe` 文件到 `out/` 目录下。
4. 创建 `taihe.driver.contexts.CompilerInstance` 实例，存储编译所依赖的主要对象，例如语言后端实例、报错信息收集器。
5. 调用 `CompilerInstance.run()` 完成编译。该函数串接了前端、语义分析、代码生成等编译流水线。
  - `CompilerInstance.collect()`: 扫描目录，收集待处理的 `.taihe` 源文件
  - `CompilerInstance.parse()`: 执行语言前端，解析 `.taihe` 源文件，并转换到 IR。
  - `CompilerInstance.validate()`: 分析语义，验证 `.taihe` 源文件的正确性。
  - `CompilerInstance.generate()`: 执行语言后端，生成目标代码。

### 文法解析

Taihe 对源码的解析基于 ANTLR 框架。`compiler/Taihe.g4` 根据 ANTLR 描述了 IDL 的文法规则，并对 ANTLR 做了扩展。

每次更新 ANTLR 文法后，需要使用 `uv build` 生成解析相关的扩展源码，位于 `taihe.parse.antlr`。
`uv build` 调用 `antlr4` 工具，生成 `TaiheLexer` 以及 `TaiheParser`，负责词法和语法分析。由于 ANTLR 缺少类型信息，Taihe 并没有直接沿用 ANTLR 的源码解析，而是又生成了更强类型的中间结构。

以 `"function foo(bar: i32)"` 为例：

1. `taihe.parse.antlr.TaiheLexer`: 分析词法，将源文件的字节流拆分成一个个 token，样例输出：
    ```python
    [KW_FUNCTION, ID("foo"), LPAREN, ID("bar"), COLON, ID("i32"), RPAREN]
    ```
2. `taihe.parse.antlr.TaiheParser`: 解析文法，将 token stream 构造为一颗原始的语法树。例如，上述例子可被拆解为：
    ```python
    from taihe.parse.antlr.TaiheParser import *
    from antlr4 import Token

    GlobalFunctionContext(
      TOKEN_name=Token("foo"),
      ParameterLst_parameters=[
        ParameterContext(
          TOKEN_decl_name=Token("bar"),
          Type_ty=ShortTypeContext(TOKEN_decl_name=Token("i32")))
      ])`
    ```
3. `taihe.parse.ast_generation.TaiheASTConverter`: 构造抽象语法树。ANTLR 内置的语法树是原始的、动态类型的，需要进一步加工，例如添加类型注解。`TaiheASTConverter` 将上述结构转换为：
    ```python
    from taihe.parse.antlr.TaiheAST import *

    GlobalFunction(
      name=TOKEN("foo")
      parameters=[
        Parameter(
          name=TOKEN("bar"),
          ty=ShortType(decl_name=TOKEN("i32")))
      ])
    ```
4. `taihe.parse.convert.AstConverter`: 转换 AST 到 IR。上述结构被继续转换为：
    ```python
    from taihe.parse.semantics.declarations import *

    GlobFuncDecl(
      name="foo",
      params=[ParamDecl(name="bar", ty_ref=TypeRefDecl(name="i32"))]
    )
    ```

### 中间表示

#### 中间表示的类型和生命周期

Taihe IR 由三部分组成：

- `taihe.semantics.declarations`：定义了“声明”的概念，例如函数、接口、结构体。
- `taihe.semantics.types`：定义了“类型”的概念，例如泛型、标量、结构体。类型不单独存储，而是依附于声明存在。
- `taihe.semantics.attributes`：定义了“属性”的概念，依附于声明而存在。Taihe IR 只表示语言无关的概念，语言相关的扩展存储于“属性”中。

Taihe IR 的生命周期是：

1. 产生：在 `CompilerInstance.parse()` 阶段，由 `taihe.parse.convert` 从源文件生成 IR，之后由语言后端的 `Backend.post_process()` 完成 IR 的后置处理。
2. 内置的语义分析：在 `CompilerInstance.validate()` 阶段，由 `taihe.semantics.analysis` 进行语义分析和检查。 **自此，IR 不再可变。**
3. 语言后端的语义分析：在 `CompilerInstance.validate()` 阶段，由 `Backend.validate()` 完成自定义的语义检查。
4. 代码生成：在 `CompilerInstance.generate()` 阶段，由 `Backend.generate()` 完成自定义的代码生成。

#### 中间表示的常见数据结构

在处理 Taihe IR 时，最常见的数据结构有：

- `Decl` 是基础类型，提供源码位置、父节点、属性存储等基础能力。一切声明均派生于此。
- `PackageDecl` 表示“包”的概念，是一组声明的容器和命名空间。
- `PackageGroup` 是一组“包”的容器，编译时常常以它作为最外层的输入。
- `TypeRefDecl` 表示声明中对类型的引用，目标类型存储于 `resolved_ty` 中

需要注意，Taihe IR 区分类型的声明和类型的引用，例如：

```python
# Taihe 文件：
#   @foo
#   enum Kind {}
#
# 对应的 IR：
kind_decl = EnumDecl("Kind", attributes=[FooAttr()])

# decl1 = StructDecl("Bar")
# Taihe 文件：
#   struct Bar {
#     k: @bar Kind
#   }
#
# 对应的 IR：
k_ty_ref = TypeRefDecl(resolved_ty=StructType(ty_decl=kind_decl), attributes=[BarAttr()])
k_field = StructFieldDecl(name="k", ty_ref=k_ty_ref)
bar_decl = StructDecl(name="Bar", fields=[k_field])
```

#### 使用 Visitor 模式访问中间表示

除了直接访问 Taihe IR 中的成员外，可以使用 `taihe.semantics.visitor` 来方便地访问：

- `DeclVisitor`：从子类到基类地分发待访问的声明。
  例如，在调用 `visitor.handle_decl(StructDecl(...))` 时，会先调用 `visit_struct_decl` 再调用 `visit_type_decl` 最后调用 `visit_decl`。覆写任意一个方法均可截获。
- `RecursiveDeclVisitor`：自顶向下地递归访问容器内的每个元素，对每个元素再从子类到基类分发。
  例如，在调用 `visitor.handle_decl(StructDecl(...))` 时，首先递归调用自己，访问每个 `StructFieldDecl`，接下来再完成原始的 `DeclVisitor` 的“子类到基类”访问。
- `TypeVisitor`：类似于 `DeclVisitor`，从子类到基类地分发待访问的类型。

可阅读 `taihe.semantics.format.PrettyPrinter` 的源码以了解详情。

#### 中间表示的性质和约束

需要注意，Taihe IR 是输入的典型（Canonical）表示，换言之，一切的 API 表示均以 IR 为准。因此，Taihe IR 具有下列性质和约束：

- 不可变：Taihe IR 在完成语义分析后不再可变。不可变的 IR 简化了各组件的设计。
- 充分：Taihe IR 充分表示了程序的输入，无需添加任何信息即可完成编译。
  例如，IR 不依附于用户的输入文件，完全可以程序直接构造。
  例如，删除 `taihe.parse` 也可以让成型的 IR 正常编译。
  或许在未来，可以将 IR 以 XML、JSON 等机器友好的格式导入或导出。
- 必要：Taihe IR 上的所有信息都是必要的，删除任何信息会导致编译失败。
  例如，不应在 IR 上存储目标语言相关的信息。
  使用 `taihe.utils.analyses` 子系统完成语言相关信息的附加。

需要说明，Taihe IR 中保存了可选的、未必完全精确的源码映射。
尽管这些信息不是必要的，但 Taihe IR 中依然保存了该信息，用于生成用户友好的报错。

#### TODO 属性：语言相关的扩展
`taihe.semantics.attributes` 将结构化的元信息附加于声明。

### 语言后端

#### 语言后端的概念和生命周期

Taihe 的目标语言生成部分位于 `taihe.driver.backend`，由一个个语言后端组成。基本概念有：

- `BackendRegistry`：存储了已知的语言后端。
- `BackendConfig`：描述了语言后端的配置信息。
  - 静态变量：包括名称、依赖的其他语言后端。这些信息被 `BackendRegistry` 使用，用来编排代码生成。
  - 动态变量：描述了语言相关的代码生成配置，这些信息存储于 `CompilerInvocation` 中，在构造 `Backend` 实例时被使用。
  - `BackendConfig` 可理解为 `Backend` 的工厂模式。
    通过将 `Backend` 解耦，可使用插件化的机制动态加载语言后端，并避免导入不使用的语言后端带来的启动速度问题。
- `Backend`：语言后端实例，在编译流水线的不同阶段被回调。

类似于前述的 IR 生命周期，Taihe 语言后端的生命周期有：

1. `taihe.cli.compiler` 初始化 `BackendRegistry`，获得已知的语言后端。
2. `taihe.cli.compiler` 根据命令行参数，配置所需的 `BackendConfig`，存入 `CompilerInvocation`。
3. `CompilerInstance` 根据 `BackendConfig` 初始化对应的 `Backend` 实例。
4. `CompilerInstance.run()` 执行编译器流程，并按需回调 `Backend` 的方法：
  - `post_process()`：完成 IR 解析（`parse`）被调用，此时可修改 IR。
  - `validate()`：在完成语义分析（`validate`）后被调用，此时不可修改 IR，但可返回错误。
  - `generate()`：在通过全部语义检查、进入代码生成（`generate`）时调用，用于生成目标代码，此时不可修改 IR。

#### 中间分析结果

Taihe 声明具有“必要”的性质，不能引入冗余的信息。
然而，语言后端往往需要引入中间分析结果，存储并在多个语言后端中共享。

举个例子，假如我们要给 `function foo(bar: i32)` 生成 C 和 C++ 侧的投影，会发现需要使用符号名称（即 "mangled name"）等 Taihe ABI 信息。
这些信息不光要在 C 中使用，也需要在 C++ 中使用；不光要在 API 作者侧使用，也需要在 API 消费者侧使用。

如果我们将函数的 Taihe ABI 信息都存储在 `GlobFuncABIInfo` 的类里面，就可以写：

```python
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager

# 编译器驱动：初始化分析管理器
am = AnalysisManager()

# 分析提供方：定义中间结果的数据结构
class GlobFuncABIInfo(AbstractAnalysis[GlobFuncDecl]):
    def __init__(self, am: AnalysisManager, f: GlobFuncDecl) -> None:
        self.mangled_name = encode(...)  # 给出中间分析结果的计算方法

# 分析消费方：从分析管理器中拉取数据
func_abi_info = GlobFuncABIInfo.get(am, func)
```

从上述例子可以看出，Taihe 引入了分析（“Analyses”）的概念，将中间分析结果和 IR 解耦。其具体实现位于 `taihe.utils.analyses`，包含下列概念：

- `AbstractAnalysis`：是一切分析中间结果的基类
- `AnalysisManager`：分析结果的缓存。由于 Taihe IR 在代码生成阶段不可变，`AnalysisManager` 缓存了相同对象的相同分析结果查询。首次查询时需要计算，后续查询时直接拿到结果。

相比于备选方案，中间分析有如下优点：

- 更好的性能：相比于使用函数计算，Analysis 可缓存计算结果，无需二次计算；相比于添加成员变量，在不生成某一语言时，无需计算和存储该语言相关的信息
- 清晰的架构。分析结果要被多方复用，相比变量或函数，以类的形式添加额外要设计类名，促进更好的架构设计。相比于直接在 IR 中添加语言相关的成员变量，Analysis 避免了多语言情况下变量爆炸和架构腐化问题。

### 语言后端的典型目录结构
`pretty-print` 在屏幕上打印格式化后的 Taihe 源文件。它是非常简单的语言后端。参考 `taihe.semantics.PrettyPrinterBackendConfig` 了解更多。

`taihe.codegen.abi` 定义了 Taihe ABI 并生成 C 文件，它是较为复杂的语言后端，结构如下：
- `mangle`：是 ABI 层的特有组件，定义了符号名称的生成算法
- `analyses`：将 Taihe IR 中的类型映射到 ABI 的类型，依赖 `mangle`
- `writer`：基于后文将介绍的 `FileWriter`，提供 C 源码的写入能力
- `gen_abi` 和 `gen_impl`：代码生成逻辑
  - 自顶向下，枚举 Taihe IR 中的每个声明
  - 基于 `analyses` 获得类型信息
  - 基于 `writer` 写入源码

### 实用工具

#### 写入目标语言的源文件
`taihe.utils.outputs` 提供了源码写入的实用能力，用于灵活组合目标语言的输出。

- `BaseWriter` 以代码行为单位，写入到文本缓冲区
  - `writelns()`：写入多个单行文本；注意，要保证每个字符串为单行
  - `with writer.indented(): ...`：写入带缩进的文本块
  - `writer.write_block()`：低性能的版本，写入可能由多行组成的文本
- `FileWriter` 继承自 `BaseWriter`；以文件为目标，支持写入文件头
  - `write_prologue()`：可重载此方法，在刚写入文件时注入内容
  - `save_as()`：保存到某个文件
  - `with ...:`：退出代码块时，若无异常则自动保存

一般情况下，语言后端需要派生 FileWriter 子类，来完成不同目标语言的支持。

此外，`BaseWriter` 支持自调试。在构造器中配置 `DebugLevel`，可在输出文本时记录调用代码的位置。

#### 生成诊断信息
`taihe.utils.diagnostics` 提供了结构化的诊断信息基础设施：

- `DiagnosticsManager`：诊断信息管理器，语义检查或语言后端可调用 `emit()` 发射一条诊断信息。
- `ConsoleDiagnosticsManager`：基于终端的诊断信息管理器，在屏幕上打印诊断信息。
- `DiagBase`: 描述了抽象的、结构化的诊断信息：
  - 可使用 `@dataclass` 存储上下文。
  - 建议填写 `loc`：用于描述诊断信息所对应的源码位置。
  - 需要重写 `describe()`：用一行简短的话描述诊断信息。
  - 可选重写 `notes()`：对这条诊断信息添加笔记（见下文）。

语义检查和语言后端一般不直接使用 `DiagBase`，而是使用派生出的类：
  - `DiagWarn` 描述了警告信息。有警告的编译依然可以继续。
  - `DiagError` 描述了错误。出现错误时，语义检查会继续运行，但不会生成代码。
    `DiagError` 也是 Python 异常，可以和 `DiagnosticsManager.capture_error()` 或 `for_each()` 联合使用。
  - `DiagFatalError` 描述了致命错误。出现致命错误时，应当立即停止语义检查和编译。
  - `DiagNote` 描述了一条笔记，可以用于显示建议。

语言无关的诊断信息都汇聚在 `taihe.utils.diagnostics`。

## TODO 运行时
