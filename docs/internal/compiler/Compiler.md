# Taihe 编译器设计文档

## 基础概念

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

## 整体流程

`taihe.cli` 负责解析命令行参数，并按需去调用编译器驱动的 Python 接口。这是因为 Taihe 编译器由一个个小小的库组成。这些库只能被 Python 代码所调用，需要封装出对外的命令行接口。

`taihe.driver` 是统筹整个流水线的编译驱动。这是因为编译流程往往包含多个小的环节，实际使用中需要保证先后顺序。例如，生成代码的前提是进行语义分析，否则编译器不知道 `function foo(x: Bar)` 中 `Bar` 的名字背后指什么类型。

在执行 `taihec` 命令时，`taihe.cli.compiler` 的 `main` 函数会被调用，完成以下流程：

1. 在 `taihe.cli.compiler` 中解析命令行参数。
2. 根据命令行参数配置构造 `taihe.driver.contexts.CompilerInvocation` 实例，描述编译意图。例如，使用 `cpp-user` 语言后端去编译 `foo.taihe` 文件到 `out/` 目录下。
3. 根据 `CompilerInvocation` 构造出 `taihe.driver.contexts.CompilerInstance` 实例，其中存储编译所依赖的主要对象，例如语言后端实例、报错信息收集器。
4. 调用 `CompilerInstance.run()` 完成编译。该函数串接了前端、语义分析、代码生成等编译流水线。
    - `CompilerInstance.collect()`: 扫描目录，收集待处理的 `.taihe` 源文件。
    - `CompilerInstance.parse()`: 执行语言前端，解析 `.taihe` 源文件，并转换到 IR。
    - `CompilerInstance.resolve()`: 将语法 IR 转换为语义 IR（名称解析、类型解析、枚举值填充、属性转换）。
    - `CompilerInstance.post_process()`: 调用语言后端的后处理钩子，在已解析的 IR 上添加后端特有的元数据。
    - `CompilerInstance.validate()`: 验证语义 IR 的正确性和一致性。
    - `CompilerInstance.generate()`: 根据 IR 生成目标语言的代码。

## 文法解析

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
     ])
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

## 中间表示

### 中间表示的类型和生命周期

Taihe IR 由三部分组成：

- `taihe.semantics.declarations`：定义了“声明”的概念，例如函数、接口、结构体。
- `taihe.semantics.types`：定义了“类型”的概念，例如泛型、标量、结构体。类型不单独存储，而是依附于声明存在。
- `taihe.semantics.attributes`：定义了“属性”的概念，依附于声明而存在。Taihe IR 只表示语言无关的概念，语言相关的扩展存储于“属性”中。

Taihe IR 的生命周期是：

1. 产生：在 `CompilerInstance.parse()` 阶段，由 `taihe.parse.convert` 从源文件生成语法 IR。
2. 解析：在 `CompilerInstance.resolve()` 阶段，由 `taihe.semantics.analysis.resolve_ir` 将语法 IR 转换为语义 IR（完成名称解析、类型解析、枚举值填充、属性转换）。
3. 后处理：在 `CompilerInstance.post_process()` 阶段，由 `Backend.post_process()` 在已解析的语义 IR 上添加后端特有的元数据（例如根据命令行选项注入默认属性）。
4. 内置的语义验证：在 `CompilerInstance.validate()` 阶段，由 `taihe.semantics.analysis.validate_ir` 进行语义检查。**自此，IR 不再可变。**
5. 语言后端的语义验证：在 `CompilerInstance.validate()` 阶段，由 `Backend.validate()` 完成自定义的语义检查。
6. 代码生成：在 `CompilerInstance.generate()` 阶段，由 `Backend.generate()` 完成自定义的代码生成。

### 中间表示的常见数据结构

在处理 Taihe IR 时，最常见的数据结构有：

- `Decl` 是基础类型，提供源码位置、父节点、属性存储等基础能力。一切声明均派生于此。
- `PackageDecl` 表示“包”的概念，是一组声明的容器和命名空间。
- `PackageGroup` 是一组“包”的容器，编译时常常以它作为最外层的输入。
- `TypeRefDecl` 表示声明中对类型的引用，目标类型存储于 `resolved_ty` 中

需要注意，Taihe IR 区分类型的声明和类型的引用，例如：

```python
# Taihe IDL 文件：
#   @foo
#   enum Kind {}
#
# 对应的 IR：
kind_decl = EnumDecl("Kind", attributes=[FooAttr()])

# decl1 = StructDecl("Bar")
# Taihe IDL 文件：
#   struct Bar {
#     k: @bar Kind;
#   }
#
# 对应的 IR：
k_ty_ref = TypeRefDecl(resolved_ty=StructType(decl=kind_decl), attributes=[BarAttr()])
k_field = StructFieldDecl(name="k", ty_ref=k_ty_ref)
bar_decl = StructDecl(name="Bar", fields=[k_field])
```

### 使用 Visitor 模式访问中间表示

除了直接访问 Taihe IR 中的成员外，可以使用 `taihe.semantics.visitor` 来方便地访问：

- `DeclVisitor`：从子类到基类地分发待访问的声明。
  例如，在调用 `visitor.handle_decl(StructDecl(...))` 时，会先调用 `visit_struct_decl` 再调用 `visit_type_decl` 最后调用 `visit_decl`。覆写任意一个方法均可截获。
- `RecursiveDeclVisitor`：自顶向下地递归访问容器内的每个元素，对每个元素再从子类到基类分发。
  例如，在调用 `visitor.handle_decl(StructDecl(...))` 时，首先递归调用自己，访问每个 `StructFieldDecl`，接下来再完成原始的 `DeclVisitor` 的“子类到基类”访问。
- `TypeVisitor`：类似于 `DeclVisitor`，从子类到基类地分发待访问的类型。

可阅读 `taihe.semantics.format.PrettyPrinter` 的源码以了解详情。

### 中间表示的性质和约束

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

### 属性：语言相关的扩展

见 [Taihe 注解系统设计文档](./AttributeSystem.md)。

## 语言后端

### 关键概念和组件

Taihe 的后端的接口定义位于 `taihe.driver.backend` 中，一个语言后端（Backend）是一个类，包含了编译器在不同阶段的回调函数。编译器在完成某个阶段时会调用语言后端的回调函数，来让语言后端完成特定的处理。

Taihe 的语言后端由以下几个组件组成：

- `BackendRegistry`：语言后端的注册表，记录了所有可用的语言后端，并负责根据从命令行参数中得到的根后端节点，递归地收集本次编译需要启用的所有语言后端。
- `BackendConfig`：描述了一个特定语言后端的配置信息。
  - `NAME`（类变量）：语言后端的名字，例如 `cpp-user`。
  - `DEPS`（类变量）：语言后端所依赖的其它语言后端。例如，`cpp-user` 依赖于 `cpp-common`。该变量中只需要列出直接依赖，由 `BackendRegistry` 负责递归地启用所有依赖。
  - `register(registry: OptionRegistry)`（类方法）：注册语言后端自有的命令行参数（`ConfigOption`）。
  - `create(options: OptionStore)`（类方法）：根据具体的命令行参数构造出结构化的语言配置实例。
  - `construct()`（实例方法）：根据语言配置构造出语言后端实例。
- `Backend`：语言后端实例，在编译流水线的不同阶段被回调。
  - `register()`：在编译器启动时被调用，此时可注册后端相关注解、分析等组件。
  - `inject()`：在完成源码收集（`collect`）后被调用，此时可注入新的文件到编译器中。
  - `post_process()`：在完成 IR 解析（`resolve`）后被调用，此时语义 IR 已完整（类型已解析、属性已转换），可在 IR 上添加后端特有的元数据。
  - `validate()`：在完成语义验证（`validate`）后被调用，此时不可修改 IR，但可报告错误。
  - `generate()`：在通过全部语义检查、进入代码生成（`generate`）时调用，用于生成目标代码，此时不可修改 IR。

### 生命周期

语言后端的生命周期与编译流程紧密相关：

1. 编译器启动时，`BackendRegistry` 根据命令行参数收集所有需要启用的语言后端，并调用它们的 `register()` 方法来将这些语言后端自有的命令行参数注册到 `OptionRegistry` 中。
2. `OptionRegistry` 根据扩展的命令行参数解析出结构化配置信息，输出到 `OptionStore` 中。
3. 启用的语言后端消费 `OptionStore` 中的配置信息，构造出语言后端配置对象，并储存在 `CompilerInvocation` 中。
4. 通过 `CompilerInvocation` 构造出 `CompilerInstance`，并在构造过程中调用语言后端配置对象上的 `construct()` 方法来构造出语言后端实例。
5. 编译器在不同阶段调用语言后端实例的回调函数，来完成注解注册、源文件注入、IR 修改、语义检查、代码生成等功能。

### 语言后端的典型目录结构

`pretty-print` 在屏幕上打印格式化后的 Taihe 源文件。它是非常简单的语言后端。参考 `taihe.semantics.PrettyPrinterBackendConfig` 了解更多。

`taihe.codegen.abi` 定义了 Taihe ABI 并生成 C 文件，它是较为复杂的语言后端，结构如下：

- `mangle`：是 ABI 层的特有组件，定义了符号名称的生成算法
- `analyses`：将 Taihe IR 中的类型映射到 ABI 的类型，依赖 `mangle`
- `attributes`：定义了 ABI 层的特有属性。
- `options`：定义了 ABI 层的特有命令行参数。
- `writer`：基于后文将介绍的 `FileWriter`，提供 C 源码的写入能力
- `gen_abi` 和 `gen_impl`：代码生成逻辑
  - 自顶向下，枚举 Taihe IR 中的每个声明
  - 基于 `analyses` 获得类型信息
  - 基于 `writer` 写入源码

### 中间分析结果

Taihe 声明具有“必要”的性质，不能引入冗余的信息。然而，语言后端往往需要引入中间分析结果，存储并在多个语言后端中共享。

举个例子，假如要给 `function foo(bar: i32)` 生成 C 和 C++ 侧的投影，会发现需要使用符号名称（即 "mangled name"）等 Taihe ABI 信息。
这些信息不光要在 C 中使用，也需要在 C++ 中使用；不光要在 API 作者侧使用，也需要在 API 消费者侧使用。

如果要将函数的 Taihe ABI 信息都存储在 `GlobFuncAbiInfo` 的类里面，就可以写：

```python
from taihe.utils.analyses import AbstractAnalysis, AnalysisManager

# 编译器驱动：初始化分析管理器
am = AnalysisManager()

# 分析提供方：定义中间结果的数据结构
@dataclass
class GlobFuncAbiInfo(AbstractAnalysis[GlobFuncDecl]):
    mangled_name: str
    # 其它 ABI 信息...

    # 覆写工厂方法 AbstractAnalysis.create(am, decl)，创建分析结果
    @classmethod
    def _create(cls, am: AnalysisManager, f: GlobFuncDecl) -> "GlobFuncAbiInfo":
        return GlobFuncAbiInfo(
            mangled_name=encode(...),
            # 其它 ABI 信息...
        )

# 分析消费方：从分析管理器中拉取数据
func_abi_info = GlobFuncAbiInfo.get(am, func)
```

从上述例子可以看出，Taihe 引入了分析（Analyses）的概念，将中间分析结果和 IR 解耦。其具体实现位于 `taihe.utils.analyses`，包含下列概念：

- `AbstractAnalysis[T]`：是一切分析中间结果的基类。
  - `T` 是分析结果所对应的 IR 声明的类型，例如 `GlobFuncDecl`。
  - `_create(am, decl)`：是工厂方法，用于创建分析结果。编译器驱动在第一次查询分析结果时会调用该方法来创建分析结果。
  - `get(am, decl)`：是查询方法，用于获取分析结果。编译器驱动在查询分析结果时会调用该方法来获取分析结果，如果分析结果不存在，则调用 `_create()` 来创建。
- `AnalysisManager`：分析结果的缓存。由于 Taihe IR 在代码生成阶段不可变，`AnalysisManager` 缓存了相同对象的相同分析结果查询。首次查询时需要计算，后续查询时直接拿到结果。
  - `provide(am, decl, analysis)`：有时一些分析结果需要由语言后端提供，此时可以调用该方法来主动提供分析结果。该方法通常在语言后端的 `post_process()` 方法中被调用，用于将一些后端配置通过分析结果的方式注入到 `AnalysisManager` 中。

相比于备选方案，中间分析有如下优点：

- 更好的性能：相比于使用函数计算，Analysis 可缓存计算结果，无需二次计算；相比于添加成员变量，在不生成某一语言时，无需计算和存储该语言相关的信息
- 清晰的架构。分析结果要被多方复用，相比变量或函数，以类的形式添加额外要设计类名，促进更好的架构设计。相比于直接在 IR 中添加语言相关的成员变量，Analysis 避免了多语言情况下变量爆炸和架构腐化问题。

## 实用工具

### 写入目标语言的源文件

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

### 生成诊断信息

`taihe.utils.diagnostics` 提供了结构化的诊断信息基础设施：

- `DiagnosticsManager`：诊断信息管理器，语义检查或语言后端可调用 `emit()` 发射一条诊断信息。
- `ConsoleDiagnosticsManager`：基于终端的诊断信息管理器，在屏幕上打印诊断信息。
- `DiagBase`: 描述了抽象的、结构化的诊断信息：
  - 可使用 `@dataclass` 存储上下文。
  - 建议填写 `loc`：用于描述诊断信息所对应的源码位置。
  - 需要重写 `describe()`：用一行简短的话描述诊断信息。
  - 可选重写 `notes()`：对这条诊断信息添加笔记（见下文）。

语义检查和语言后端一般不直接使用 `DiagBase`，而是使用派生出的类：

- `DiagWarn`：描述了警告信息。有警告的编译依然可以继续。
- `DiagError`：描述了错误。出现错误时，语义检查会继续运行，但不会生成代码。另外，它也继承了 `Exception` 类，可以被抛出，可以和 `DiagnosticsManager.capture_error()` 或 `for_each()` 联合使用。
- `DiagFatalError`：描述了致命错误。出现致命错误时，应当立即停止语义检查和编译。
- `DiagNote`：表示一条提示，可以用于显示建议。

语言无关的诊断信息都汇聚在 `taihe.utils.diagnostics`。
