# 编译器流程知识

本文只记录 `CompilerInstance` 的阶段顺序、状态转移和失败短路。IR 数据结构见 `Compiler_IR_Design_Knowledge_Base_CN.md`，扩展钩子见 `Compiler_Extensibility_Knowledge_Base_CN.md`，公共工具的使用时段见 `Compiler_Utils_Knowledge_Base_CN.md`。

## 主链路

| 阶段 | 状态转移 | 使用的基础设施 | 阶段边界 |
| --- | --- | --- | --- |
| `setup` | 编译参数到后端实例 | `OptionRegistry`、`AttributeRegistry`、`AnalysisManager`、`OutputManager` | 只注册和构造，不读取 IR。 |
| `collect` | 输入路径到 `SourceManager` | 源码和诊断管理器 | 后端可添加源文件，不解析内容。 |
| `parse` | `SourceManager` 到语法 IR | 解析器和诊断管理器 | 不依赖名称和类型解析。 |
| `resolve` | 语法 IR 到语义 IR | 注解和诊断管理器 | 完成名称、类型和注解解析。 |
| `post_process` | 语义 IR 到后端附加状态 | Analysis、后端自有注解 | 不修改 IR 结构，不依赖后端顺序。 |
| `validate` | 语义 IR 到诊断结论 | 诊断管理器和 Analysis | 只检查，不修复输入。 |
| `generate` | 已验证 IR 到输出 | `OutputManager` 和 writer | 有错误则跳过；不再做语义判断。 |
| `post_generate` | 已记录输出到构建元数据 | `OutputManager` | 所有后端生成完成后统一执行。 |

## 控制流约束

- `collect`、`parse`、`resolve` 按固定顺序执行；后续阶段不得补做前序工作，否则会读取不完整状态。
- `resolve` 后存在诊断错误时必须跳过 `post_process`、`validate` 和 `generate`。
- `post_process`、`validate`、`generate` 中的后端执行顺序不得成为可观察依赖，否则改变后端启用顺序会改变结果。
- 语义验证和后端验证属于同一检查阶段；两者均不得改变 IR 结构。
- 输出只能在 `generate` 阶段产生，并由 `OutputManager.post_generate()` 完成跨后端收尾，避免失败编译留下被登记的产物。

## 修改前检查

| 问题 | 决策 |
| --- | --- |
| 新工作最早在哪个阶段信息完备？ | 放在该阶段，不要提前读取未解析状态。 |
| 失败是否应阻止后续阶段？ | 用户错误通过诊断管理器触发统一短路。 |
| 是否需要后端参与？ | 使用已有钩子；不要在编译驱动中写目标语言逻辑。 |
| 是否产生文件或构建元数据？ | 只进入 `generate` / `post_generate`。 |

## 代码和测试

| 主题 | 锚点 |
| --- | --- |
| 流水线与状态持有 | `compiler/taihe/driver/contexts.py` |
| 解析转换 | `compiler/taihe/parse/` |
| 解析和验证步骤 | `compiler/taihe/semantics/analysis.py` |
| 后端阶段契约 | `compiler/taihe/driver/backend.py` |
| 详细设计 | `docs/internal/compiler/Compiler.md` |
| 前端和语义验证 | `compiler/tests/` |