# Taihe 注解系统设计文档

## 设计目标

Taihe 注解系统用于为抽象语法树（AST）中的声明对象（`Decl` 及其子类）附加可验证的注解系统，提供：

- 结构化、可扩展的注解定义体系；
- 类型安全的注解系统，通过统一但可自定义的机制自动校验注解参数和上下文等；
- 声明类型限定的注册机制，某些注解只能作用于特定类型的声明；
- 清晰的错误提示与建议。

## 核心类与结构

核心概念包括 `Argument`、`UncheckedAttribute`、`CheckedAttribute`、`AttributeRegistry` 等。

```
AnyAttribute
├── UncheckedAttribute
└── AbstractCheckedAttribute
    └── AutoCheckedAttribute
        ├── TypedAttribute
        └── RepeatableAttribute
```

### `Argument`

表示 `UncheckedAttribute` 的参数，包含位置、参数名称和参数值等信息。

它的成员包括：

- `loc: SourceLocation`：参数在源代码中的位置。
- `key: str`：参数名，如果是关键字参数则为其名称，否则为 `None`。
- `value: float | bool | int | str`：参数值。

### `UncheckedAttribute`

表示从源代码中直接解析出来，但尚未经过任何语义分析或验证的原始注解。

它的成员包括：

- `name: str`：注解在 IDL 中的名称（不含 `@` 或 `@!` 前缀）。
- `args: list[Argument]`：参数列表，包括位置参数和关键字参数。

它支持的方法包括：

- `consume(cls, decl: Decl) -> Iterable[Self]`：返回一个 `UncheckedAttribute` 的迭代器，该迭代器会从传入的 `decl` 上依次获取并删除 `UncheckedAttribute`，直到没有为止。

### `AbstractCheckedAttribute`

经过验证的注解的抽象基类，定义了自定义注解所需实现的底层框架。

包括以下核心方法：

- `try_construct(cls, raw: UncheckedAttribute, dm: DiagnosticsManager) -> Self | None`：抽象类工厂方法，传入一个 `raw`，对其进行参数验证，从而构造强类型的具体 `CheckedAttribute` 实例。此外该方法还会传入一个 `dm`，用于输出创建中产生的错误信息。如果构造成功则应返回该 `CheckedAttribute` 对象，否则返回 `None`。_注意，这一阶段的检查完全是上下文无关的，即不会考虑其所在的上下文中是否支持使用该注解。_
- `check_context(self, parent: Decl, dm: DiagnosticsManager) -> None`：抽象成员方法。会传入当前 `CheckedAttribute` 所在的 `parent`，并基于此对当前 `CheckedAttribute` 进行上下文检查：包括检查该注解是否支持在当前上下文使用，是否和其他注解冲突等。此外该方法也会传入 `dm` 用于输出创建中产生的错误信息。_注意，这一函数会在所有其他语义分析完成后调用，所以我们可以确保包括类型解析等在这一阶段已经完成，且整个 IR 中的所有注解都已经被解析为 `CheckedAttribute`。_

### `AutoCheckedAttribute[ParentDecl]`

继承自 `AbstractCheckedAttribute`，为其中的抽象方法提供了默认实现，自动处理基于 `dataclass` 的参数解析和基础的上下文检查逻辑。

泛型参数：

- `ParentDecl`：表示该注解可以附加的声明类型，必须是 `Decl` 的子类（支持联合类型）。

需要定义以下类变量：

- `NAME: ClassVar[str]`：注解名称，用于注册和查找。
- `TARGETS: ClassVar[tuple[type[ParentDecl], ...]]`：一个元组，表示该注解可以附加的所有 `Decl` 的子类型，该属性应与泛型参数 `ParentDecl` 保持一致。
- `ATTRIBUTE_GROUP_TAGS: ClassVar[frozenset[AttributeGroupTag]]`：可选，一组**互斥标签**。如果两个注解共享了至少一个相同的标签，它们就不能同时附加到同一个声明上。

`AutoCheckedAttribute` 为 `try_construct` 和 `check_context` 方法提供了默认实现，并提供以下可覆写的方法：

- `try_construct_from_parsed_args(cls, args: list[Argument], kwargs: dict[str, Argument], dm: DiagnosticsManager, *, loc: SourceLocation | None) -> Self | None`：`try_construct` 方法的默认实现会先解析原始 `UncheckedAttribute` 对象，得到其匿名参数列表 `args` 和关键字参数字典 `kwargs` 后再调用该方法来创建 `CheckedAttribute` 对象。该方法的默认实现中则会根据当前 `dataclass` 的字段定义进行参数匹配和类型检查，并尝试构造实例。如果需要自定义参数解析逻辑，可以覆写该方法。
- `check_typed_context(self, parent: ParentDecl, dm: DiagnosticsManager) -> None`：该方法会被 `check_context` 调用，`check_context` 方法的默认实现会先通过 `isinstance` 检查 `parent` 的类型是否在 `TARGETS` 中，然后将被保证为 `ParentDecl` 的 `parent` 传入该方法。该方法的默认实现中会根据 `ATTRIBUTE_GROUP_TAGS` 检查互斥组冲突。后端开发者可以覆写该方法以实现更复杂的上下文检查逻辑。

注意，由于 `try_construct_from_parsed_args` 方法中会使用 `dataclass` 的字段定义进行参数匹配和类型检查，因此 `AutoCheckedAttribute` 的子类必须是 `dataclass`。

### `TypedAttribute[ParentDecl]`

继承自 `AutoCheckedAttribute` 的泛型类，表示在单个声明对象上最多只能出现一次的注解。该类覆写了 `check_typed_context()` 方法，增加了额外的检查以确保在同一个 `parent` 上不会有多个该注解的实例，如果存在则报告错误。
  
提供的方法：

- `get(cls, decl: ParentDecl) -> Self | None`：用于获取某个声明对象上的该注解实例，如果不存在则返回 `None`。

### `RepeatableAttribute[ParentDecl]`

继承自 `AutoCheckedAttribute` 的泛型类，表示在单个声明对象上可以出现多次的注解。

提供的方法：

- `get_all(cls, decl: ParentDecl) -> list[Self]`：用于获取某个声明对象上的该注解实例列表，如果不存在则返回空列表。

### `AttributeRegistry`

用于注册注解以及构造 `CheckedAttribute`。`AttributeRegistry` 和 `CompilerInstance` 关联，语言后端在创建时会将自己的注解注册到 `AttributeRegistry` 中。

核心方法：

- `register(self, *attr_types: CheckedAttrT) -> None`：注册注解类。
- `attach(self, raw: UncheckedAttribute, dm: DiagnosticsManager) -> AbstractCheckedAttribute | None`：接收未处理的原始注解，根据其 `name` 字段在注册表中查找已注册的注解类，并调用其 `try_construct` 方法进行构造。如果找不到对应的注解类，或者构造失败，则返回 `None`。

## 和外部概念的交互

- `AstConverter`：`AstConverter` 会在 AST 转换阶段将 AST 上的注解节点转换为 `UncheckedAttribute`，并存储到父节点上。

  path: **taihe/parse/convert.py**

- `CompilerInstance`：`CompilerInstance` 中包含 `AttributeRegistry` 成员变量，用于注册和管理由不同语言后端定义的注解。

  path: **taihe/driver/contexts.py**

- `BackendConfig`：在 `BackendConfig` 给 `CompilerInstance` 创建后端时，会同时将自己的相关注解注册到 `CompilerInstance` 中的 `AttributeRegistry` 中。

  path: **taihe/codegen/xxx/**init**.py**

- `Decl`：语义层的核心抽象，代表所有声明类实体，会记录当前语法元素上的 `UncheckedAttribute` 或者 `CheckedAttribute`。

  path: **taihe/semantics/declarations.py**

- `_ConvertAttrPass`：将 `UncheckedAttribute` 转换为 `CheckAttribute`，即调用 `try_construct` 方法，并将其存储到其所在的声明对象上。

  path: **taihe/semantics/analysis.py**

- `_CheckAttrPass`：调用 `CheckedAttribute` 上的 `check_context` 方法对 `CheckedAttribute` 进行上下文检查。

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

1. 在 `CompilerInstance` 的初始化阶段创建 `AttributeRegistry`；
2. 在根据 `BackendConfig` 以此构造相应语言后端的同时，调用 `AttributeRegistry` 上的 `register` 方法，注册该语言后端支持的全部注解；
3. 在语法解析阶段，将 AST 上的注解节点转换为 `UncheckedAttribute`, 并记录在相应的父节点上；
4. 在语义分析阶段：
   1. `_ConvertAttrPass` 阶段，调用 `AttributeRegistry` 的 `attach` 方法，将 `UncheckedAttribute` 转换为 `CheckedAttribute`，并存储到其所在的声明对象上；
   2. `_CheckAttrPass` 阶段，调用每个 `CheckedAttribute` 上的 `check_context` 方法对 `CheckedAttribute` 进行上下文检查；
5. 在相应语言后端自己的语义分析和代码生成逻辑中，使用对应的具体注解类的 `get` 方法获取注解。

## 如何为新语言后端添加注解

以下通过一个完整的示例，展示如何为新的语言后端添加、注册和使用自定义注解。

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

在语言后端的初始化或配置方法中，获取 `CompilerInstance` 的 `AttributeRegistry` 并注册所有注解。

```python
from taihe.driver.contexts import CompilerInstance
from .attributes import all_attr_types


class MyLanguageBackend(Backend):
    def __init__(self, ci: CompilerInstance):
        # ...
        ci.attribute_registry.register(*all_attr_types)
```

### 第三步：处理

在语义分析或代码生成的后续阶段，你可以通过 `get()` 或 `get_all()` 方法安全地获取并使用这些注解。

```python
# 示例：在一个分析 Pass 中处理 PackageDecl
def process_package(package_decl: PackageDecl):
    # 使用 get() 获取 NamespaceAttr 实例
    if namespace_attr := NamespaceAttr.get(package_decl):
        print(f"Package module: {namespace_attr.module}")
        if namespace_attr.namespace:
            print(f"Package namespace: {namespace_attr.namespace}")

# 示例：在一个分析 Pass 中处理函数
def process_function(func_decl: GlobFuncDecl):
    # 检查是否存在 @get 注解
    if get_attr := GetAttr.get(func_decl):
        prop_name = get_attr.member_name or get_attr.func_suffix
        print(f"Function '{func_decl.name}' is a getter for property '{prop_name}'.")

    # 检查是否存在 @set 注解
    if set_attr := SetAttr.get(func_decl):
        prop_name = set_attr.member_name or set_attr.func_suffix
        print(f"Function '{func_decl.name}' is a setter for property '{prop_name}'.")
```
