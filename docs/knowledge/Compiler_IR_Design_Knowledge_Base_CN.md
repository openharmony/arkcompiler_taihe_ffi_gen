# 编译器 IR 设计知识

本文只记录 Taihe IR 的数据模型、状态和结构约束。IR 在各阶段何时产生和冻结见 `Compiler_Pipeline_Knowledge_Base_CN.md`；注解扩展见 `Compiler_Extensibility_Knowledge_Base_CN.md`。

## 数据模型

| 组成 | 作用 | 关键边界 |
| --- | --- | --- |
| `PackageGroup` / `PackageDecl` | 编译单元根和命名空间容器 | 包身份不等于文件路径或目标模块路径。 |
| `Decl` 层次 | 声明、成员、参数、引用和源码位置 | 父子关系表达结构所有权。 |
| `Type` 层次 | 已解析类型语义 | 类型对象不保存某次使用位置的信息。 |
| `TypeRefDecl` | 类型使用位置及其解析状态 | 定义、语义类型和使用位置是三个身份。 |
| 已检查注解 | 附着于声明的强类型扩展信息 | 注解所有权属于注册方，不是任意字典。 |
| `Visitor` | 对声明和类型层次进行分发和遍历 | 遍历策略不进入 IR 数据类。 |

## 状态边界

| 状态 | 可依赖信息 | 禁止假设 |
| --- | --- | --- |
| 语法 IR | 结构、原始名字、未检查注解、源码位置 | 名称和 `TypeRefDecl` 已解析。 |
| 已解析语义 IR | 绑定后的名字和类型、强类型注解 | 后端附加信息已经提供。 |
| 后处理后的 IR | 语义 IR 加后端自有注解或外部 Analysis | 其他后端执行顺序或结果可见。 |
| 已验证 IR | 所有启用检查均通过 | 后续阶段还会修复语义。 |

## 结构约束

- IR 只保存完成编译所需的语言无关事实；目标符号、平台句柄和输出路径不得进入核心字段，否则共享 IR 会依赖具体后端。
- `TypeRefDecl` 必须显式区分未解析、解析失败和解析成功；不要用 `None` 同时表示多种状态。
- 源码位置允许缺失或不精确，只服务诊断；不要把文件路径当作语义身份。
- 后端附加信息优先使用 Analysis；只有需要参与注解生命周期和上下文检查时才使用强类型注解，避免扩大共享 IR。
- 新增 IR 节点或层次时必须同步检查 `Visitor` 分发、格式化、解析和验证。

## 修改前检查

| 问题 | 决策 |
| --- | --- |
| 新字段是否是所有后端共享且不可重新推导的事实？ | 否则不要进入核心 IR。 |
| 数据描述定义、类型还是使用位置？ | 分别归属 `TypeDecl`、`Type`、`TypeRefDecl`。 |
| 节点是否改变树结构或继承层次？ | 同步检查父节点、`Visitor` 和递归遍历。 |
| 信息能否作为 Analysis 惰性计算？ | 能则不要扩大 IR 数据结构。 |

## 代码和测试

| 主题 | 锚点 |
| --- | --- |
| 声明和引用 | `compiler/taihe/semantics/declarations.py` |
| 类型 | `compiler/taihe/semantics/types.py` |
| 注解载体 | `compiler/taihe/semantics/attributes.py` |
| Visitor 和格式化 | `compiler/taihe/semantics/visitor.py`, `compiler/taihe/semantics/format.py` |
| 详细设计 | `docs/internal/compiler/IRDesign.md`, `docs/internal/compiler/AttributeSystem.md` |
| 验证 | `compiler/tests/` |