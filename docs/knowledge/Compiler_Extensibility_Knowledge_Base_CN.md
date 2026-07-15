# 编译器扩展机制知识

本文只记录编译选项、注解、`BackendConfig` 和后端钩子等扩展协议。阶段顺序见 `Compiler_Pipeline_Knowledge_Base_CN.md`；Analysis 和输出框架本身见 `Compiler_Utils_Knowledge_Base_CN.md`。

## 扩展链路

| 扩展输入 | 声明与校验位置 | 注入时机 | 消费位置 |
| --- | --- | --- | --- |
| 编译选项 | `BackendConfig.register_options_to()`；`from_options()` 完成值与组合校验 | 构造 `BackendConfig` | 后端实例或后端提供的 Analysis。 |
| 注解类型 | `Backend.setup()` 注册；注解系统完成参数和目标检查 | `resolve` 时原始注解转为强类型注解 | `validate`、Analysis 或生成器。 |
| 附加源文件 | 后端配置决定来源 | `Backend.add_sources()` | 与普通源文件一起解析。 |
| 派生信息 | 后端定义 Analysis 类型 | 惰性 `get()` 或在 `post_process()` 中 `provide()` | `validate` 和 `generate`。 |
| 输出文件 | 后端生成器声明输出 | `Backend.generate()` | 通过公共 `OutputManager` 写入。 |

## 所有权边界

| 信息 | 唯一所有者 | 常见误用 |
| --- | --- | --- |
| 原始命令行值 | `OptionRegistry` 解析过程 | 不要传入 Analysis 或生成器深处重复解析。 |
| 已验证后端配置 | `BackendConfig` | 不要挂到共享 IR 或工具层全局状态。 |
| 语言无关语义 | 语义 IR | 不要用后端注解覆盖核心语义事实。 |
| 后端派生数据 | 后端 Analysis 或强类型注解 | 不要为单个目标扩展 IR 字段。 |
| 文件内容与路径 | 生成器和 `OutputManager` | 不要在 `resolve` / `validate` 阶段写文件。 |

## 阶段约束

- `BackendConfig.from_options()` 必须完成选项合法性检查；`build()` 不得再报告输入错误。
- `setup()` 只注册扩展能力；不要读取尚未收集和解析的 IR，否则扩展会依赖未建立的编译状态。
- `post_process()` 只提供后端私有派生信息且必须幂等；不要重写共享语义或其他后端注解，否则后端顺序会影响结果。
- `validate()` 只报告后端约束错误；不得修改 IR 或缓存来“修复”输入。
- `generate()` 只消费已验证数据并产生输出；不得首次报告可预见的用户错误，否则可能留下部分产物。
- 扩展可以定义 Analysis，但不得让 `AnalysisManager` 依赖具体 `BackendConfig`。

## 修改前检查

| 问题 | 决策 |
| --- | --- |
| 新数据是否对所有后端都成立？ | 否则进入后端 Analysis、注解或私有结构，不进入核心 IR。 |
| Analysis 是否依赖无默认值的配置？ | 在 `post_process()` 显式 `provide()`；key 规则见 Utils 知识。 |
| 错误最早在哪个阶段可确定？ | 在该阶段诊断，不要推迟到 `generate`。 |
| 扩展是否写文件或产生外部副作用？ | 只允许在 `generate` 或专门输出管理阶段发生。 |

## 代码和测试

| 主题 | 锚点 |
| --- | --- |
| 后端协议和实例 | `compiler/taihe/driver/backend.py`, `compiler/taihe/driver/contexts.py` |
| 选项系统 | `compiler/taihe/driver/options.py` |
| 注解系统 | `compiler/taihe/semantics/attributes.py` |
| 公共工具契约 | `docs/knowledge/Compiler_Utils_Knowledge_Base_CN.md` |
| 验证 | `compiler/tests/`, `test/` |