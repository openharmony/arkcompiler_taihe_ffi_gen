# Taihe IR 设计文档

## 1. 概述

### 1.1. IR 在 Taihe 编译器中的定位

Taihe IR（中间表示）是一个用于描述和操作结构化接口定义的类型系统和声明模型。它提供了一个强类型、层次化、可扩展的中间表示，用于支持接口定义语言（IDL）的静态分析、代码生成和跨语言互操作。

IR 的核心使命是：将前端解析出的语法结构，提升为一套与具体语法无关，且类型安全、可进行严格语义分析、并能最终被多个语言后端消费以生成目标代码的核心数据模型。

### 1.2. 核心设计原则

Taihe IR 的整体架构和具体实现遵循以下核心设计原则：

* **强类型系统**：IR 自身是一个强类型的 Python 对象模型。所有声明和类型都由明确的类来表示，利用 Python 的类型系统在开发阶段就能发现大量潜在错误。
* **结构化与层次化**：IR 采用严格的树状层次结构，通过父子关系精确表示 IDL 的作用域和从属关系，为上下文分析和遍历提供了坚实基础。
* **关注点分离**：严格分离了不同层面的抽象。
  * **声明与类型分离**：`declarations.py` 定义“是什么”（如结构体声明），`types.py` 定义其“作为类型时的语义”。
  * **定义与使用分离**：通过 `TypeRefDecl` 等引用节点，将一个类型的定义与其在代码中的使用分离开来。
  * **语言无关性**：IR 核心只包含语言无关的语义信息，任何特定于目标语言的逻辑都由语言后端通过属性系统或中间分析来处理。
* **位置跟踪**：精确的源代码位置跟踪，用于诊断和错误报告
* **属性系统**：可扩展的元数据注解机制
* **访问者模式**：支持类型和声明的可扩展操作

### 1.3. 系统架构概览

Taihe IR 由三个紧密协作的核心组件构成，它们共同定义了 IDL 程序的完整语义：

1. **声明系统**：定义了程序的所有结构化实体，如包、接口、函数、字段等。
2. **类型系统**：定义了所有数据类型的语义和关系。
3. **属性系统**：IR 的扩展机制，允许向声明节点附加可验证的、结构化的元数据。

## 2. 类型系统

* 文件：`semantics/types.py`

类型系统提供了丰富的类型表示和操作能力，支持静态类型检查和代码生成。

### 2.1 类型层次结构

类型系统基于以下层次结构：

```
Type                       # 所有类型的基类
├── VoidType               # void 类型
└── NonVoidType            # 非 void 类型
    ├── BuiltinType        # 内置类型
    │   ├── UnitType       # 单元类型
    │   ├── ScalarType     # 标量类型 (bool, i32, f64 等)
    │   ├── StringType     # 字符串类型
    │   └── OpaqueType     # 不透明类型
    ├── GenericType        # 泛型类型
    │   ├── ArrayType      # 数组类型
    │   ├── OptionalType   # 可选类型
    │   ├── VectorType     # 向量类型
    │   ├── MapType        # 映射类型
    │   └── SetType        # 集合类型
    ├── CallbackType       # 回调类型
    └── UserType           # 用户定义类型
        ├── EnumType       # 枚举类型
        ├── StructType     # 结构体类型
        ├── UnionType      # 联合类型
        └── IfaceType      # 接口类型
```

### 2.2. 类型构造机制

* **内置类型**：通过一个全局字典 `BUILTIN_TYPES` 进行注册和查找，将字符串标识符（如 "i32"）映射到对应的 `ScalarType` 构造器。
* **泛型类型**：通过 `BUILTIN_GENERICS` 字典进行查找，将泛型名称（如 "Vector"）映射到对应的泛型类型构造器，然后传入类型参数进行实例化。
* **用户类型**：由对应的 `TypeDecl`（如 `IfaceDecl`）的 `as_type()` 方法创建，将声明与其类型语义绑定。

## 3. 声明系统

* 文件：`semantics/declarations.py`

声明系统是 Taihe IR 的核心组件，定义了程序的结构元素。

### 3.1 声明层次结构

声明系统基于一个灵活的类层次结构，包括：

```
Decl                            # 所有声明的基类
├── PackageDecl                 # 包声明
├── PackageRefDecl              # 包引用
├── DeclarationRefDecl          # 声明引用
├── ImportDecl                  # 导入声明
│   ├── PackageImportDecl       # 包导入
│   └── DeclarationImportDecl   # 声明导入
├── TypeRefDecl                 # 类型引用
│   ├── ImplicitTypeRefDecl     # 隐式类型引用（如缺省的返回值类型等）
│   └── ExplicitTypeRefDecl     # 显式类型引用
│       ├── ShortTypeRefDecl    # 短类型引用（e.g. "Foo", "i32"）
│       ├── LongTypeRefDecl     # 长类型引用（e.g. "my.pkg.Foo"）
│       ├── GenericTypeRefDecl  # 泛型类型引用（e.g. "Vector<i32>"）
│       └── CallbackTypeRefDecl # 回调类型引用（e.g. "(arg: i32) => void"）
├── GenericArgDecl              # 泛型参数
├── ParamDecl                   # 参数声明
├── EnumItemDecl                # 枚举项
├── StructFieldDecl             # 结构体字段
├── UnionFieldDecl              # 联合类型字段
├── IfaceMethodDecl             # 接口方法
├── IfaceExtendDecl             # 接口继承
└── PackageLevelDecl            # 包级声明
    ├── GlobFuncDecl            # 全局函数
    └── TypeDecl                # 类型声明
        ├── EnumDecl            # 枚举
        ├── StructDecl          # 结构体
        ├── UnionDecl           # 联合类型
        └── IfaceDecl           # 接口

NamedFunctionLikeDecl = GlobFuncDecl | IfaceMethodDecl
FunctionLikeDecl = NamedFunctionLikeDecl | CallbackTypeRefDecl
TypeHolderDecl = FunctionLikeDecl
               | ParamDecl
               | StructFieldDecl
               | UnionFieldDecl
               | EnumDecl
               | IfaceExtendDecl
               | GenericArgDecl
```

此外，`PackageGroup` 用于表示多个包的集合，支持跨包引用解析。

### 3.2 类型引用

`TypeRefDecl` 的设计是 IR 的一个核心亮点。它将一个类型的声明（`TypeDecl`），类型本身（`Type`），以及类型的使用（`TypeRefDecl`）三者分离开来。

* **动机**：
    1. **延迟解析**：在前端解析阶段，一个类型引用（如 `foo: MyType`）的目标 `MyType` 尚未被解析或定义。`TypeRefDecl` 作为一个占位符，使得解析过程可以继续，而将符号解析的逻辑推迟到语义分析阶段。
    2. **上下文元数据**：类型引用可能携带与其使用相关的上下文信息（如源代码位置、属性等），这些信息不应污染类型本身或其声明。
    3. **清晰的语义**：明确区分了类型的定义、实际类型对象、以及类型的使用位置，使得 IR 更加清晰和易于分析。

* **实现**：所有持有 `TypeRefDecl` 的声明对象（即 `TypeHolderDecl`）都有以下三个方法：
    1. `resolve_ty`：该方法接收一个 `SpecificType | None` 参数，表示解析后的具体类型。应在类型解析阶段调用此方法，调用后会将 `TypeRefDecl` 的 `resolved_ty_or_none` 字段设置为该类型，并将其 `is_resolved` 标记为 `True`。如果传入 `None`，则表示解析失败，但 `is_resolved` 仍然会被设置为 `True`，以避免重复解析。
    2. `ty_or_none`：该属性返回 `TypeRefDecl` 当前解析的类型（`SpecificType`）或 `None`（如果尚未解析或解析失败）。
    3. `ty`：该属性返回 `TypeRefDecl` 当前解析的类型（`SpecificType`）。如果尚未解析或解析失败，则抛出异常。该属性通常只能在代码生成阶段使用，此时应该能保证所有类型引用都已成功解析。

注意，由于不同上下文中可以使用的类型是不同的，所以上面所说的 `SpecificType` 针对不同 `TypeHolderDecl` 对应不同的类型。例如，对于 `EnumDecl`，`SpecificType` 是 `ScalarType | StringType`；对于 `ParamDecl`，`SpecificType` 则是 `NonVoidType`。这使得类型的正确性可以在类型解析阶段得到静态、严格的保证，并在代码生成阶段简化逻辑。

## 4. 属性系统

* 文件：`semantics/attributes.py`

属性系统提供了一种灵活、类型安全的机制，用于向声明添加元数据注解。

### 4.1 属性层次结构

属性系统基于以下层次结构：

```
AnyAttribute                             # 所有属性的基类
├── UncheckedAttribute                   # 未经检查的原始属性
└── AbstractCheckedAttribute             # 经过检查的属性的抽象基类
    └── AutoCheckedAttribute[DeclT]      # 自动检查的属性
        ├── TypedAttribute[DeclT]        # 单次使用的类型化属性
        └── RepeatableAttribute[DeclT]   # 可重复使用的类型化属性
```

此外，还有以下核心概念：

* `AttributeRegistry`：用于注册注解以及构造 `CheckedAttribute`。`AttributeRegistry` 和 `CompilerInstance` 关联，语言后端在创建时会将自己的注解注册到 `AttributeRegistry` 中。

### 4.2. 设计核心：两阶段验证生命周期

1. **解析阶段 (`UncheckedAttribute`)**: 前端在解析 `@` 语法时，会创建原始的、未经验证的 `UncheckedAttribute` 对象。它只记录了属性名和原始的参数列表。
2. **语义分析阶段 (`AbstractCheckedAttribute`)**:
    * **上下文无关检查**：`AttributeRegistry` 查找与属性名匹配的已注册 `CheckedAttribute` 类，并调用其 `try_construct` 工厂方法。此方法对 `UncheckedAttribute` 的参数进行严格的**上下文无关检查**（如参数个数、类型、顺序、关键字等）。
    * **上下文相关检查**：构造成功后，强类型的 `CheckedAttribute` 实例会替换掉 `UncheckedAttribute`。随后，该实例的 `check_context` 方法被调用，进行**上下文相关检查**（如该属性是否能附加在当前 `Decl` 类型上，是否与其他属性冲突）。

这种两阶段生命周期将语法解析、参数验证和上下文验证清晰地分离开来，使得每一步的职责都非常单一，极大地提高了系统的健壮性和可维护性。

### 4.3. 易用性设计：`AutoCheckedAttribute`

为了简化新属性的定义，系统提供了 `AutoCheckedAttribute`。开发者只需将其子类定义为 Python 的 `dataclass`，`AutoCheckedAttribute` 的基类实现就能自动提供 `try_construct` 和 `check_context` 的默认逻辑，极大地减少了定义新属性所需的样板代码。`TypedAttribute` 和 `RepeatableAttribute` 进一步区分了单次使用和可重复使用的场景。

## 5. 访问者模式

访问者模式是遍历和操作 Taihe IR 的标准方式，其设计尤为精巧，提供了极大的灵活性。

### 5.1. 设计动机与优势

* **解耦操作与数据**：将对 IR 的操作（如代码生成、语义检查、格式化打印）从 IR 数据类本身中分离出来。这遵循了“开闭原则”，当需要添加新操作时，只需实现一个新的 Visitor，而无需修改稳定的 IR 类。
* **多态分发**：通过在每个 IR 节点上实现 `accept(visitor)` 方法，可以实现对不同类型节点的双重分发，确保调用 Visitor 上最精确匹配的 `visit_...` 方法。

### 5.2. 核心设计：继承体系驱动的层次化分发

Taihe 的 Visitor 设计最特殊之处在于，**Visitor 的类继承体系与 IR 节点的类继承体系是镜像的，并利用这一结构实现了强大的层次化分发（Hierarchical Dispatch）**。

以 `TypeVisitor` 为例：
`TypeVisitor` -> `NonVoidTypeVisitor` -> `BuiltinTypeVisitor` -> `ScalarTypeVisitor`

* `ScalarTypeVisitor` 定义了 `visit_scalar_type`。
* `BuiltinTypeVisitor` 继承了 `ScalarTypeVisitor`，并将 `visit_scalar_type` 的实现重定向到 `visit_builtin_type`。
* `NonVoidTypeVisitor` 继承了 `BuiltinTypeVisitor`，并将 `visit_builtin_type` 的实现重定向到 `visit_non_void_type`。
* `TypeVisitor` 继承了 `NonVoidTypeVisitor`，并将 `visit_non_void_type` 的实现重定向到 `visit_type`。

当在一个 `ScalarType` 节点上调用 `accept(my_visitor)` 时，会触发 `my_visitor.visit_scalar_type(self)`。其行为取决于 `my_visitor` 的实现：

1. **精确处理**：如果 `my_visitor` 重写了 `visit_scalar_type`，则该方法被直接调用。
2. **分类处理**：如果 `my_visitor` 未重写 `visit_scalar_type` 但重写了 `visit_builtin_type`，则调用会沿着继承链“上浮”，最终执行 `visit_builtin_type`。这允许开发者只用一个方法就处理所有内置类型。
3. **通用处理**：如果只重写了 `visit_type`，则所有类型的访问最终都会汇集于此。

这种设计赋予了开发者极大的灵活性，可以根据需要选择处理的粒度，从最具体的节点到最抽象的基类。

### 5.3. `RecursiveDeclVisitor`

系统还提供了一个便利的 `RecursiveDeclVisitor`。它继承自 `DeclVisitor`，并重写了所有容器类型节点（如 `PackageDecl`, `StructDecl` 等）的 `visit_...` 方法，在其中递归地对其子节点调用 `accept(self)`。这为需要进行全树深度优先遍历的场景（如代码生成、全局分析）提供了一个开箱即用的解决方案。
