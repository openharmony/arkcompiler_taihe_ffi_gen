# Attribute 系统设计文档

## 设计目标

该 Attribute 系统用于为抽象语法树( AST )中的声明对象(Decl 及其子类)附加可验证的 Attribute，提供：

- 结构化、可扩展的 Attribute 定义体系;

- 类型安全的参数校验, 包括参数个数和参数类型;

- 声明类型限定的注册机制, 某些 Attribute 只能作用于特定类型的声明;

- 清晰的错误提示与建议。

## 核心类与结构

核心概念有4个，`Argument`、`UncheckedAttribute`、`CheckedAttribute`、`AttributeManager`

### `Argument`

目前 attribute 的参数支持 float、bool、int、str 四种类型

```python
@dataclass
class Argument:

    loc: Optional[SourceLocation]
    key: str
    value: float | bool | int | str
```

`Argument` 的位置信息可以提供更加细粒度更加友好的报错信息

`Argument` 可以表示普通的 argument 也可以表示 keyword argument，当表示普通 argument 时，key 为空字符串

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

### `CheckedAttribute`

经过相关检查的 Attribute

AbstractCheckedAttribute: Base class for validated attributes
    └── AutoCheckedAttribute: Automatic checking via configuration
        ├── TypedAttribute: Single-use attributes with type checking
        └── RepeatableAttribute: Multi-use attributes with type checking

在 analyze_semantics 阶段将 IR上 Decl的 `UncheckedAttribute` 转换为 `CheckedAttribute`，转换过程进行相关检查

相关检查包括：参数数量检查，参数重复赋值检查，参数类型检查，Attribute 注册检查，Attribute 互斥检查，Decl 检查

核心方法：

(1)`try_construct()`，进行参数数量检查，参数重复赋值检查，参数类型检查，Attribute 互斥检查

(2)`get()`，用于获取一个 Decl 上的 Attribute(s)

### `AttributeManager`

用于注册 Attribute 以及构造 `CheckedAttribute`

核心方法：

(1) `register()`, 注册 Attribute

(2) `attach()`, 输入 `UnCheckedAttribute` 以及 `Decl`，构造`CheckedAttribute`

## 相关概念交互

### `CompilerInstance`

path: taihe/driver/contexts.py

`CompilerInstance` 有一个成员变量为 `AttributeManager`

### `BridgeBackendConfig`

path: taihe/codegen/xxx/\_\_init\_\_.py

具体语言后端的 Config 给 `CompilerInstance`实例 register 对应语言后端的 attribute

### `Decl`

path: taihe/semantics/declarations.py

`Decl` 类是语义层的核心抽象, 代表所有声明类实体, 在不同阶段承载 `UnCheckedAttribute` 以及 `CheckedAttribute`

### `AstConverter`

path: taihe/parse/convert.py

`AstConverter` 有一个成员变量为 `AttributeManager`

`create_uncheck_attr` 方法把 AST (抽象语法树)中 attribute 转换为 `UnCheckedAttribute`

### `analyze_semantics`

path: taihe/semantics/analysis.py

`_ConvertAndCheckAttrPass` 将 `UnCheckedAttribute` 转换为 `CheckAttribute`

### `DiagError`

path: taihe/utils/exceptions.py

Attribute系统中用于报告错误的诊断类继承自 `DiagError`, 具体诊断类有 `AttrArgCountError`,`AttrArgOrderError`,`AttrArgReAssignError`,`AttrArgTypeError`,`AttrArgUndefError`,`AttrMutuallyExclusiveError`,`AttrRepeatError`,`AttrUndefError`, 用于输出相关错误信息

## 总体流程

- 1 在 `CompilerInstance` 创建阶段创建 `AttributeManager`;

- 2 在语言后端的 `BackendConfig` 创建对应语言后端的 Backend 阶段，
使用 `AttributeManager` 的 `register()` 方法将对应语言后端的 Attribute 注册到 `AttributeManager`;

- 3 在 `AstConverter` 阶段, 将 AST 上的 Attribute 节点转换为 `UncheckedAttribute`, 并存储到父节点的 `Decl` 上;

- 4 在 semantics 的 analysis 阶段，使用 `AttributeManager` 的 `attach()` 方法，
将 `Decl` 节点的 `UncheckedAttribute` 转换为 `AbstractCheckedAttribute`;

- 5 在对应语言后端的 codegen 的 analyses 阶段，使用对应的具体 Attribute 类的 `get()` 方法获取 Attribute.


## 如何为新语言后端添加 attribute

主要分为 3 步，第一步是定义 attribute ，第二步是注册 attribute ，第三步是处理 attribute

1 定义 attribute

```python
# 定义新的 attribute

# 如果希望某个参数是必须参数，样例如下：
class StaticAttr(TypedAttribute):
    NAME = "static"
    TARGETS = frozenset({GlobFuncDecl})

    cls_name: str


# 如果希望某个参数是可选参数，需要设置默认值为 None, 样例如下：
class GetAttr(TypedAttribute):
    NAME = "get"
    TARGETS = frozenset({GlobFuncDecl, IfaceMethodDecl})

    member_name: str | None = None


class SetAttr(TypedAttribute):
    NAME = "set"
    TARGETS = frozenset({GlobFuncDecl, IfaceMethodDecl})

    member_name: str | None = None

# 定义互斥集
GetAttr.MUTUALLY_EXCLUSIVE = frozenset({SetAttr})
SetAttr.MUTUALLY_EXCLUSIVE = frozenset({GetAttr})

# 保存所有该语言后端的attribute列表用于注册
all_attr_types: list[CheckedAttrT] = [
    StaticAttr,
    GetAttr,
    SetAttr,
]
```

2 注册 attribute

在对应语言后端 BackendConfig 给 `CompilerInstance` 实例 register 对应语言后端的 attribute

```python
instance.attribute_manager.register(*all_attr_types)
```

3 处理 attribute

在 analyses 阶段，通过具体 Attribute 类的`get`方法来获取 attribute
