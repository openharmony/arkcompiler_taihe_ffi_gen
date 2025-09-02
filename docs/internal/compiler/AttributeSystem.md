# Taihe 注解系统设计文档

## 设计目标

Taihe 注解系统用于为抽象语法树（AST）中的声明对象（Decl 及其子类）附加可验证的注解系统，提供：

- 结构化、可扩展的注解定义体系；
- 类型安全的参数校验，包括参数个数和参数类型；
- 声明类型限定的注册机制，某些注解只能作用于特定类型的声明；
- 清晰的错误提示与建议。

## 核心类与结构

核心概念包括 `Argument`、`UncheckedAttribute`、`CheckedAttribute`、`AttributeRegistry`：

```
AnyAttribute
├── UncheckedAttribute
└── AbstractCheckedAttribute
    └── AutoCheckedAttribute
        ├── TypedAttribute
        └── RepeatableAttribute
```

- `Argument`：表示 `UncheckedAttribute` 的参数，包含位置、键和值等信息。

  它的成员包括：
  - `loc`：参数在源代码中的位置。
  - `key`：参数名，如果是关键字参数则为其名称，否则为 `None`。
  - `value`：参数值，可以是 `float`、`bool`、`int` 或 `str` 等类型。

- `UncheckedAttribute`：原始的弱类型的注解，包含名称、位置和参数列表等信息。它是 AST 转换阶段的中间表示，未经过参数类型检查。

  它的成员包括：
  - `name`：注解的名称。
  - `loc`：注解在源代码中的位置。
  - `args`：参数列表，包含位置参数和关键字参数。

  在 convert 阶段会将原始 AST 转换为 IR，此阶段会将注解节点转换为 `UncheckedAttribute`，它支持的方法包括：
  - `consume()`，用于获取一个 `UncheckedAttribute` 的迭代器，该迭代器会从 `Decl` 依次获取并删除 `UncheckedAttribute`，直到没有为止。

- `CheckedAttribute`：强类型注解。在 `analyze_semantics` 阶段将 IR 上 `Decl` 的 `UncheckedAttribute` 转换为 `CheckedAttribute`，转换过程进行参数个数、类型等检查，确保符合预期。

  包括以下核心方法：
  - `try_construct()`：类工厂方法，对 `UncheckedAttribute` 进行参数个数、类型等检查，从而构造强类型的具体 `CheckedAttribute` 实例。_注意，这一阶段的检查完全是上下文无关的，即不考虑其所在的 `Decl` 是否支持该注解，该方法在 `AutoCheckedAttribute` 中存在默认实现，会假设其子类为 `dataclass`，并根据其上的字段进行参数个数、类型等检查。_
  - `check_context()`：对 `CheckedAttribute` 进行上下文检查，检查其所在的 `Decl` 是否支持该注解，这一函数会在所有其他语义分析完成后调用，所以我们可以确保包括类型解析已经完成，所有注解都已经被解析为 `CheckedAttribute`。
  - `check_typed_context()`：存在于 `AutoCheckedAttribute` 上，类似于 `check_context()`，但其所在的 `Decl` 已经被保证为正确的类型。
  - `get()`：存在于 `TypedAttribute` 上，用于获取一个 `Decl` 上此类型的注解实例，如果不存在则返回 `None`。
  - `get()`：存在于 `RepeatableAttribute` 上，用于获取一个 `Decl` 上此类型的注解实例列表。

- `AttributeRegistry`：用于注册注解以及构造 `CheckedAttribute`。

  核心方法：
  - `register()`：注册注解。
  - `attach()`：输入 `UncheckedAttribute`，根据 `name` 在注册表中查找相应的 `CheckedAttribute`，并调用其上的 `try_construct()` 方法构造 `CheckedAttribute`。

## 相关概念交互

- `AstConverter`：`AstConverter` 会在 AST 转换阶段将 AST 上的注解节点转换为 `UncheckedAttribute`，并存储到父节点的 `Decl` 上。

  path: **taihe/parse/convert.py**

- `CompilerInstance`：`CompilerInstance` 中包含 `AttributeRegistry` 成员变量，用于注册和管理由不同语言后端定义的注解。

  path: **taihe/driver/contexts.py**

- `BackendConfig`：在 `BackendConfig` 给 `CompilerInstance` 创建后端时，会同时将自己的相关注解注册到 `CompilerInstance` 中的 `AttributeRegistry` 中。

  path: **taihe/codegen/xxx/**init**.py**

- `Decl`：语义层的核心抽象，代表所有声明类实体，会记录当前语法元素上的 `UncheckedAttribute` 或者 `CheckedAttribute`。

  path: **taihe/semantics/declarations.py**

- `_ConvertAttrPass`：将 `UncheckedAttribute` 转换为 `CheckAttribute`，即调用 `try_construct()` 方法，并将其存储到 `Decl` 上。

  path: **taihe/semantics/analysis.py**

- `_CheckAttrPass`：调用 `CheckedAttribute` 上的 `check_context()` 方法对 `CheckedAttribute` 进行上下文检查。

  path: **taihe/semantics/analysis.py**

- `DiagError`：注解系统中用于报告错误的诊断类继承自 `DiagError`。

  其中，和 `_ConvertAttrPass` 阶段相关的诊断类有：
  - `AttrNotExistError`：该名称的注解不存在或未注册
  - `AttrArgOrderError`：注解参数顺序错误
  - `AttrArgRedefError`：注解参数重复定义
  - `AttrArgMissingError`：注解缺少必需参数
  - `AttrArgUnrequiredError`：注解参数过多
  - `AttrArgTypeError`：注解参数类型错误

  和 `_CheckAttrPass` 阶段相关的诊断类包括：
  - `AttrConflictError`：该注解与其他注解冲突
  - `AttrTargetError`：该注解不支持当前声明类型

  path: **taihe/utils/exceptions.py**

## 编译器处理注解的完整流程

1. 在 `CompilerInstance` 创建阶段创建 `AttributeRegistry`；

2. 在语言后端的 `BackendConfig` 创建对应语言后端的 Backend 阶段，使用 `AttributeRegistry` 的 `register()` 方法将对应语言后端的注解注册到 `AttributeRegistry`；

3. 在 `AstConverter` 阶段，将 AST 上的注解节点转换为 `UncheckedAttribute`, 并存储到父节点的 `Decl` 上；

4. 在 semantics 的 analysis 阶段，使用 `AttributeRegistry` 的 `attach()` 方法，将 `Decl` 节点的 `UncheckedAttribute` 转换为 `AbstractCheckedAttribute`；

5. 在对应语言后端的代码生成相关逻辑中，使用对应的具体注解类的 `get()` 方法获取注解。

## 如何为新语言后端添加注解

主要分为三步，分别为定义、注册、和处理。

### 第一步：定义注解

以下是一个示例，定义了 `NamespaceAttr`，`GetAttr` 和 `SetAttr` 三个注解。

```python
@dataclass
class NamespaceAttr(TypedAttribute[PackageDecl]): # 继承自 TypedAttribute，指定目标 Decl 类型只能为 PackageDecl
    NAME = "namespace"  # 定义注解的名称
    TARGETS = (PackageDecl,)  # 目标类型元组

    module: str  # 必须参数
    namespace: str | None = None  # 可选参数


# 定义一个互斥组标签，用于标记使用该标签的注解互斥
FUNCTION_TYPE_ATTRIBUTE_GROUP = AttributeGroupTag()

@dataclass
class GetAttr(TypedAttribute[GlobFuncDecl | IfaceMethodDecl]):
    NAME = "get"
    TARGETS = (GlobFuncDecl, IfaceMethodDecl)
    ATTRIBUTE_GROUP_TAGS = frozenset({FUNCTION_TYPE_ATTRIBUTE_GROUP})

    member_name: str | None = None
    func_suffix: str = field(default="", init=False)  # 不需要在初始化时传入的参数

    @override
    def check_typed_context(
        self,
        parent: GlobFuncDecl | IfaceMethodDecl,
        dm: DiagnosticsManager,
    ) -> None:  # 覆写 check_typed_context 方法进行上下文检查
        # 检查函数参数和返回值类型
        if len(parent.params) != 0 or parent.return_ty_ref is None:
            dm.emit(
                AdhocError(
                    f"Attribute '{self.NAME}' can only be attached to functions with no parameters and a return type.",
                    loc=self.loc,
                )
            )
        # 检查成员名称是否指定
        if self.member_name is None:
            if len(parent.name) > 3 and parent.name[:3].lower() == "get":
                self.func_suffix = parent.name[3:]
            else:
                dm.emit(
                    AdhocError(
                        f"Attribute '{self.NAME}' requires the property name to be specified when the function name does not start with 'get'.",
                        loc=self.loc,
                    )
                )
        # 调用父类方法进行其他检查
        super().check_typed_context(parent, dm)


@dataclass
class SetAttr(TypedAttribute[GlobFuncDecl | IfaceMethodDecl]):
    NAME = "set"
    TARGETS = (GlobFuncDecl, IfaceMethodDecl)
    ATTRIBUTE_GROUP_TAGS = frozenset({FUNCTION_TYPE_ATTRIBUTE_GROUP})

    member_name: str | None = None
    func_suffix: str = field(default="", init=False)  # 不需要在初始化时传入的参数

    @override
    def check_typed_context(
        self,
        parent: GlobFuncDecl | IfaceMethodDecl,
        dm: DiagnosticsManager,
    ) -> None:  # 覆写 check_typed_context 方法进行上下文检查
        # 检查函数参数和返回值类型
        if len(parent.params) != 1 or parent.return_ty_ref is not None:
            dm.emit(
                AdhocError(
                    f"Attribute '{self.NAME}' can only be attached to functions with one parameter and no return type.",
                    loc=self.loc,
                )
            )
        # 检查成员名称是否指定
        if self.member_name is None:
            if len(parent.name) > 3 and parent.name[:3].lower() == "set":
                self.func_suffix = parent.name[3:]
            else:
                dm.emit(
                    AdhocError(
                        f"Attribute '{self.NAME}' requires the property name to be specified when the function name does not start with 'set'.",
                        loc=self.loc,
                    )
                )
        # 调用父类方法进行其他检查
        super().check_typed_context(parent, dm)


# 保存所有该语言后端的注解列表用于注册
all_attr_types: list[CheckedAttrT] = [
    NamespaceAttr,
    GetAttr,
    SetAttr,
]
```

### 第二步：注册

在对应语言后端 BackendConfig 给 `CompilerInstance` 实例 register 对应语言后端的注解：

```python
instance.attribute_regsitry.register(*all_attr_types)
```

### 第三步：处理

在 analyses 阶段，通过具体注解类的 `get` 方法来获取注解：

```python
# 获取 PackageDecl 上的 NamespaceAttr
namespace_attrs = NamespaceAttr.get(package_decl)
```
