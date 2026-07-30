# Taihe 指引

## 项目定位

本仓库是 Taihe 语言、编译器、运行时、标准库、测试和示例的源码树根目录。优先按这些目录定位问题：

- `compiler/`：IDL 前端、语义 IR、编译驱动、后端框架和代码生成实现。
- `runtime/`：跨语言 ABI 所需的 C/C++ 运行时、头文件分层和对象模型基础设施。
- `stdlib/`：编译器内置或后端注入的标准 IDL 定义。
- `test/`：生成代码、运行时和跨语言互操作的端到端测试。
- `cookbook/`：公开行为的示例工程，不替代 `test/` 中的回归测试。
- `docs/public/`、`docs/internal/`、`docs/knowledge/`：公开规格、内部设计文档和 Agent 知识库。
- `scripts/`、`cmake/`：构建、检查、测试和 CMake 集成脚本。

## 构建和验证

以下命令均从仓库根目录执行。

```sh
# 同步 Python 开发环境
uv sync

# 构建 Python 包；修改 compiler/Taihe.g4 后必须重新生成 ANTLR 产物
uv build

# 代码格式与类型检查
scripts/check
```

```sh
# 默认测试集合：pytest、C++ 用户、ANI 用户、CMake、NAPI 用户
scripts/test

# 编译器前端和语义测试
scripts/test --run pytest

# C++、ANI、NAPI 用户测试
scripts/test --run core            # C++ 用户；单工程使用 -u cpp
scripts/test --run ani             # ANI 用户；单工程使用 -u sts
scripts/test --run napi            # NAPI 用户；单工程使用 -u ts

# 单个端到端工程
taihe-tryit test -u cpp test/rgb
taihe-tryit test -u sts test/ani_primitives
taihe-tryit test -u ts test/napi_primitives
```

修改 `compiler/Taihe.g4` 后必须运行 `uv build`。涉及设备、平台 SDK 或服务集成的行为，必须补充实际环境证据。

## 知识索引

稳定背景知识放在 `docs/knowledge/`。改动前按场景读取对应文件：

| 场景 | 先读 |
| --- | --- |
| 源码树、模块所有权、语言/编译器/ABI/运行时边界、文档分层 | `docs/knowledge/Project_Overview_Knowledge_Base_CN.md` |
| IR 声明和类型、TypeRefDecl、注解载体、Visitor、数据结构 | `docs/knowledge/Compiler_IR_Design_Knowledge_Base_CN.md` |
| 编译阶段、状态转移、失败短路、工具使用时段 | `docs/knowledge/Compiler_Pipeline_Knowledge_Base_CN.md` |
| 注解、Options、BackendConfig、后端依赖和 hooks | `docs/knowledge/Compiler_Extensibility_Knowledge_Base_CN.md` |
| Analysis、诊断、异常、Outputs、Writer | `docs/knowledge/Compiler_Utils_Knowledge_Base_CN.md` |
| 公共基础、调用、对象、容器、平台运行时、作者入口和平台桥分层 | `docs/knowledge/Runtime_Architecture_Knowledge_Base_CN.md` |
| 运行时数据类型与内存模型、类型映射、对象/句柄、接口投影和调用适配 | `docs/knowledge/Runtime_Type_Protocols_Knowledge_Base_CN.md` |
| pytest、集成测试、taihe-tryit、CMake、验证证据选择 | `docs/knowledge/Validation_Strategy_Knowledge_Base_CN.md` |

## 项目约束

- 必须把 `AGENTS.md` 保持为入口层，只放路由、全局命令和全局硬约束；不要在此展开领域知识。
- 必须把稳定设计约束写入 `docs/knowledge/`；不要写入临时状态、具体后端当前实现细节或教程式说明。
- 不要把目标语言或平台特有信息写入语言无关 IR；优先通过注解系统、Analysis 或后端私有结构承载。
- 修改 `compiler/Taihe.g4` 必须运行 `uv build`，并补充前端或语义验证。
- 新增 `test/` 或 `cookbook/` 子目录必须同步注册到对应 `CMakeLists.txt`。