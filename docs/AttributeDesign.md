# Attribute 系统设计文档

## 设计目标

该 Attribute 系统用于为抽象语法树( AST )中的声明对象(Decl 及其子类)附加可验证的 Attribute，提供：

- 结构化、可扩展的 Attribute 定义体系;

- 类型安全的参数校验, 包括参数个数和参数类型;

- 声明类型限定的注册机制, 某些 Attribute 只能作用于特定类型的声明;

- 清晰的错误提示与建议。

## 核心类与结构

核心概念有4个，`Argument`、`UncheckedAttribute`、`CheckedAttribute`、`AttributeManager`

```
AnyAttribute
├── UncheckedAttribute
└── AbstractCheckedAttribute
    └── AutoCheckedAttribute
        ├── TypedAttribute
        └── RepeatableAttribute
```

### `Argument`

目前 attribute 的参数支持 float、bool、int、str 四种类型

```python
@dataclass
class Argument:
    loc: Optional[SourceLocation]
    key: str | None
    value: float | bool | int | str
```

`Argument` 的位置信息可以提供更加细粒度更加友好的报错信息

`Argument` 可以表示 positional argument 或 keyword argument，当表示 positional argument 时，key 为 None

### `UncheckedAttribute`

原始 Attribute 信息，未进行相关检查

```python
@dataclass
class UncheckedAttribute:
    name: str
    loc: Optional[SourceLocation]
    args: Sequence[Argument]
```

在 convert 阶段会将原始 AST 转换为 IR，此阶段会将 Attribute 节点转换为 `UncheckedAttribute`

支持的方法：

- `consume()`，用于获取一个 `UncheckedAttribute` 的迭代器，
  该迭代器会从 `Decl` 依次获取并删除 `UncheckedAttribute`，直到没有为止

### `CheckedAttribute`

经过相关检查的 Attribute

在 analyze_semantics 阶段将 IR上 Decl的 `UncheckedAttribute` 转换为 `CheckedAttribute`，转换过程进行相关检查

相关检查包括：参数数量检查，参数重复赋值检查，参数类型检查，Attribute 注册检查，Attribute 互斥检查，Decl 检查

核心方法：

- `try_construct()`，对 `UncheckedAttribute` 进行参数个数、类型等检查，构造 `CheckedAttribute`，注意这一阶段的检查完全是上下文无关的，即不考虑其所在的 `Decl` 是否支持该 Attribute，该方法在 `AutoCheckedAttribute` 中存在默认实现，会假设其子类为 `dataclass`，并根据其上的字段进行参数个数、类型等检查

- `check_context()`，对 `CheckedAttribute` 进行上下文检查，检查其所在的 `Decl` 是否支持该 Attribute，这一函数会在所有其他语义分析完成后调用，所以我们可以确保包括类型解析已经完成，所有注解都已经被解析为 `CheckedAttribute`

- `check_typed_context()`，存在于 `AutoCheckedAttribute` 上，类似于 `check_context()`，但其所在的 `Decl` 已经被保证为正确的类型

- `get()`，存在于 `TypedAttribute` 和 `RepeatableAttribute` 上，用于获取一个 `Decl` 上此类型的 Attribute(s)

### `AttributeManager`

用于注册 Attribute 以及构造 `CheckedAttribute`

核心方法：

- `register()`, 注册 Attribute

- `attach()`, 输入 `UnCheckedAttribute` 以及 `Decl`，构造`CheckedAttribute`

## 相关概念交互

### `CompilerInstance`

- path: taihe/driver/contexts.py

`CompilerInstance` 有一个成员变量为 `AttributeManager`

### `BridgeBackendConfig`

- path: taihe/codegen/xxx/\_\_init\_\_.py

具体语言后端的 Config 给 `CompilerInstance`实例 register 对应语言后端的 attribute

### `Decl`

- path: taihe/semantics/declarations.py

`Decl` 类是语义层的核心抽象, 代表所有声明类实体, 在不同阶段承载 `UnCheckedAttribute` 以及 `CheckedAttribute`

### `AstConverter`

- path: taihe/parse/convert.py

`AstConverter` 有一个成员变量为 `AttributeManager`

`create_uncheck_attr` 方法把 AST (抽象语法树)中 attribute 转换为 `UnCheckedAttribute`

### `analyze_semantics`

- path: taihe/semantics/analysis.py

`_ConvertAttrPass` 将 `UnCheckedAttribute` 转换为 `CheckAttribute`，即调用 `try_construct()` 方法，并将其存储到 `Decl` 上；`_CheckAttrPass` 调用 `check_context()` 方法对 `CheckedAttribute` 进行上下文检查

### `DiagError`

- path: taihe/utils/exceptions.py

Attribute系统中用于报告错误的诊断类继承自 `DiagError`, 具体诊断类有 `AttrArgCountError`,`AttrArgOrderError`,`AttrArgReAssignError`,`AttrArgTypeError`,`AttrArgUndefError`,`AttrMutuallyExclusiveError`,`AttrRepeatError`,`AttrUndefError`, 用于输出相关错误信息

## 总体流程

1. 在 `CompilerInstance` 创建阶段创建 `AttributeManager`;

2. 在语言后端的 `BackendConfig` 创建对应语言后端的 Backend 阶段，使用 `AttributeManager` 的 `register()` 方法将对应语言后端的 Attribute 注册到 `AttributeManager`;

3. 在 `AstConverter` 阶段, 将 AST 上的 Attribute 节点转换为 `UncheckedAttribute`, 并存储到父节点的 `Decl` 上;

4. 在 semantics 的 analysis 阶段，使用 `AttributeManager` 的 `attach()` 方法，将 `Decl` 节点的 `UncheckedAttribute` 转换为 `AbstractCheckedAttribute`;

5. 在对应语言后端的 codegen 的 analyses 阶段，使用对应的具体 Attribute 类的 `get()` 方法获取 Attribute.


## 如何为新语言后端添加 attribute

主要分为 3 步，第一步是定义 attribute ，第二步是注册 attribute ，第三步是处理 attribute

1. 定义 attribute

```python
@dataclass
class NamespaceAttr(TypedAttribute[PackageDecl]): # 继承自 TypedAttribute，指定目标 Decl 类型只能为 PackageDecl
    NAME = "namespace"  # 定义 attribute 的名称
    TARGETS = (PackageDecl,)  # 目标类型元组

    module: str  # 必须参数
    namespace: str | None = None  # 可选参数


# 定义一个互斥组标签，用于标记使用该标签的 attribute 互斥
FUNCTION_TYPE_ATTRIBUTE_GROUP = AttributeGroupTag()

@dataclass
class GetAttr(TypedAttribute[GlobFuncDecl | IfaceMethodDecl]):
    NAME = "get"
    TARGETS = (GlobFuncDecl, IfaceMethodDecl)
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({FUNCTION_TYPE_ATTRIBUTE_GROUP})

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
    MUTUALLY_EXCLUSIVE_GROUP_TAGS = frozenset({FUNCTION_TYPE_ATTRIBUTE_GROUP})

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


# 保存所有该语言后端的attribute列表用于注册
all_attr_types: list[CheckedAttrT] = [
    NamespaceAttr,
    GetAttr,
    SetAttr,
]
```

2. 注册 attribute

在对应语言后端 BackendConfig 给 `CompilerInstance` 实例 register 对应语言后端的 attribute

```python
instance.attribute_manager.register(*all_attr_types)
```

3. 处理 attribute

在 analyses 阶段，通过具体 Attribute 类的 `get` 方法来获取 attribute
