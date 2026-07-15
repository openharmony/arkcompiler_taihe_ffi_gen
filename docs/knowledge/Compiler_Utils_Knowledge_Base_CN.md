# 编译器公共工具知识

本文只记录编译流程和后端共用的 Analysis、诊断、异常与输出框架。各工具的使用阶段见 `Compiler_Pipeline_Knowledge_Base_CN.md`，后端注入方式见 `Compiler_Extensibility_Knowledge_Base_CN.md`。

## 工具边界

| 工具 | 负责 | 不负责 |
| --- | --- | --- |
| `AnalysisManager` | 按 `(analysis type, hashable arg)` 缓存派生对象 | IR 所有权、配置解析、跨编译持久化。 |
| `DiagnosticsManager` | 聚合严重级别、输出诊断、批量捕获 `DiagError` | 修复 IR、吞掉内部编程错误。 |
| `DiagError` / `DiagFatalError` | 表达可定位、可恢复或需终止的用户输入问题 | 替代 `AssertionError`、`TypeError` 等内部不变量错误。 |
| `OutputManager` | 打开输出、记录生成/运行时文件、生成后收尾 | 决定目标语言内容。 |
| `BaseWriter` / `FileWriter` | 缩进、块结构、调试来源和缓冲写入 | 路径策略和语义判断。 |

## Analysis 缓存协议

| 场景 | key | 创建方式 | 约束 |
| --- | --- | --- | --- |
| IR 节点派生结果 | 对应 `Decl`、`Type` 或 `PackageGroup` | 首次 `get()` 调用 `_create()` | 缓存键必须稳定且可哈希。 |
| 外部配置决定且无默认值 | 对应 IR 节点 | 数据提供方在使用前调用 `provide()` | 缺失时不要静默构造默认值。 |
| 与 IR 无关的静态规则 | 不使用 Analysis | 常量或注册表 | 不污染单次编译缓存。 |

## 错误处理协议

- 用户输入导致且可继续收集的问题必须发出 `DiagError`；不要用普通异常中断整次分析，否则无法继续收集诊断。
- `DiagnosticsManager.for_each()` 只适合可逐元素恢复的处理步骤；存在全局不变量时不要继续。
- `DiagFatalError` 表示后续处理没有意义；普通语义错误不要升级为该异常。
- 断言和普通 Python 异常只用于编译器内部不变量；不要把用户可触发路径当作内部崩溃。

## 输出协议

- 后端只通过 `OutputManager` 打开和登记文件；不要自行拼接根输出目录，否则构建元数据会遗漏文件。
- `FileWriter` 当前在异常退出时仍提交已缓冲内容；不要把 writer 上下文当作事务或回滚边界。
- 生成文件和运行时源文件必须记录到正确分组；构建系统依赖这些分组生成元数据。
- 跨后端汇总必须放在 `post_generate()`；不要假设某个后端最后执行，否则改变后端顺序会产生不完整汇总。

## 修改前检查

| 问题 | 决策 |
| --- | --- |
| 派生数据的身份由什么决定？ | 用最小且稳定的可哈希对象作为 Analysis 缓存键。 |
| 错误来自用户输入还是内部不变量？ | 前者诊断，后者异常或断言。 |
| 输出是否需要进入构建元数据？ | 选择正确分组并通过 `OutputManager` 记录。 |

## 代码和测试

| 主题 | 锚点 |
| --- | --- |
| Analysis | `compiler/taihe/utils/analyses.py` |
| Diagnostics | `compiler/taihe/utils/diagnostics.py`, `compiler/taihe/utils/exceptions.py` |
| Outputs / Writers | `compiler/taihe/utils/outputs.py` |
| Sources | `compiler/taihe/utils/sources.py` |
| 详细设计 | `docs/internal/compiler/CompilerUtils.md` |