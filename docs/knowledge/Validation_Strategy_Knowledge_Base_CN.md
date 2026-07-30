# 验证策略知识

本文只记录“某类改动需要什么证据”，不重复 `AGENTS.md` 中的命令速查。编译器阶段边界见 `Compiler_Pipeline_Knowledge_Base_CN.md`，运行时风险见 `Runtime_Architecture_Knowledge_Base_CN.md` 与 `Runtime_Type_Protocols_Knowledge_Base_CN.md`。

## 证据选择

| 改动面 | 最小可执行证据 | 必须升级验证的条件 | 测试锚点 |
| --- | --- | --- | --- |
| 语法、AST 转换 | 重新生成 ANTLR 产物并运行相关 pytest | 改变合法输入或生成 IR 时，追加语义和端到端用例 | `compiler/Taihe.g4`, `compiler/tests/` |
| 名称、类型、注解、诊断 | 正向或负向 pytest | 行为依赖后端或标准库注入时，追加对应集成工程 | `compiler/tests/`, `test/` |
| 后端 Analysis、映射、生成器 | 单个相关工程先生成，再测试 | 共享后端基础设施或输出契约变化时，运行对应测试组 | `test/`, `cookbook/` |
| 核心 C++ 用户链路 | `core` 测试组或单工程 `taihe-tryit test -u cpp` | 改动共享 ABI、运行时或构建逻辑时，追加受影响平台测试组 | `test/rgb/`, `test/object/` |
| ANI 用户链路 | `ani` 测试组；单工程使用 `taihe-tryit test -u sts` | 涉及设备、平台 SDK 或服务时，补充真实环境证据 | `test/ani_*/` |
| NAPI 用户链路 | `napi` 测试组；单工程使用 `taihe-tryit test -u ts` | 涉及设备、平台 SDK 或服务时，补充真实环境证据 | `test/napi_*/` |
| 运行时头、ABI 布局、生命周期 | 最小 CMake 或端到端工程 | 改变公开布局、所有权或析构路径时，追加兼容和异常路径证据 | `runtime/`, `test/` |
| CMake/打包/资源 | 对应构建目标或 `cmake` 测试组 | 安装布局或资源发现变化时，从干净目录验证 | `cmake/`, `scripts/build`, `compiler/tests/test_resources.py` |
| 文档和知识库 | Markdown 诊断、`git diff --check`、锚点存在性 | 命令或路径变化时，对照实现核验 | `AGENTS.md`, `docs/knowledge/` |

## 测试资产边界

| 资产 | 只适合验证 | 不要用于替代 |
| --- | --- | --- |
| `compiler/tests/` | 前端、语义、诊断和编译器工具的进程内行为 | 生成代码编译、运行时和跨语言互操作。 |
| `test/` | 生成、编译、链接、执行和错误工程的回归 | 公开用法说明。 |
| `cookbook/` | 用户可见能力的可运行示例 | `test/` 中的负向或回归覆盖。 |
| `scripts/test` | 仓库约定的测试组编排 | 单个失败点的最短反馈；先缩小到 pytest 或单工程。 |
| `taihe-tryit` | 单工程生成、构建和执行 | 多工程覆盖与干净环境构建。 |

## 约束规则

- 必须先运行能否定当前修改假设的最小测试，再扩到测试组；原因：全量结果难以定位局部错误。
- 修改语法后必须重新生成 ANTLR 产物；不要用旧生成文件的测试结果作为证据。
- 新增 `test/` 或 `cookbook/` 工程必须注册到对应 `CMakeLists.txt`；未进入常规编排的工程不算回归覆盖。
- CMake 结果与源码变化不一致时必须从干净构建目录复验；不要把缓存命中当作成功证据。
- 平台 SDK、设备或服务相关行为只适合用真实环境证据闭环；主机侧生成成功不足以证明运行行为。

## 修改前检查

| 问题 | 决策 |
| --- | --- |
| 最小测试能否覆盖修改实际经过的路径？ | 不能则直接选择包含该路径的单工程或测试组。 |
| 改动是否跨越解析、生成、运行时边界？ | 每个被跨越的边界至少需要一项证据。 |
| 测试是否依赖生成产物或 CMake 缓存？ | 是则确认生成步骤已执行，并评估是否需要干净构建。 |
| 用户可见能力是否新增或改变？ | 在 `test/` 回归之外同步更新或增加 cookbook。 |

## 代码和测试

| 主题 | 锚点 |
| --- | --- |
| 测试组定义 | `scripts/test` |
| 单工程工具 | `compiler/taihe/cli/tryit.py` |
| Python 检查 | `scripts/check`, `pyproject.toml` |
| 工程注册 | `test/CMakeLists.txt`, `cookbook/CMakeLists.txt` |
| 构建集成 | `CMakeLists.txt`, `cmake/`, `scripts/build` |