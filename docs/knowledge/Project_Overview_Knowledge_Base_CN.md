# 项目总览知识

本文只记录 Taihe 源码树的整体模型、模块所有权和文档分层。编译器与运行时设计分别见对应知识文件；语言使用规则以 `docs/public/spec/` 为准。

## 系统模型

| 层次 | 输入与输出 | 源码所有者 | 稳定边界 |
| --- | --- | --- | --- |
| IDL 语言 | `.taihe` 源码到语言语义 | `compiler/Taihe.g4`, `compiler/taihe/parse/`, `compiler/taihe/semantics/` | 不包含目标语言投影规则。 |
| 编译器驱动 | 编译意图到已验证 IR 和输出调度 | `compiler/taihe/driver/` | 不承载具体后端业务逻辑。 |
| 后端 | 语义 IR 到目标源码 | `compiler/taihe/codegen/` | 不反向改变语言核心语义。 |
| ABI | 语言无关的二进制表示与调用契约 | `compiler/taihe/codegen/abi/`, `runtime/include/taihe/*.abi.h` | 编译器生成与运行时定义必须一致。 |
| C++ 投影与运行时 | ABI 到 C++ 类型、所有权和调用接口 | `runtime/include/taihe/`, `runtime/src/` | 核心层保持平台无关。 |
| 标准声明 | 编译器或平台桥依赖的标准 IDL | `stdlib/` | 不放项目临时模型。 |

## 文件分层

| 目录 | 适合内容 | 不要放入 |
| --- | --- | --- |
| `docs/knowledge/` | 修改代码前需要的路由、边界和硬性规则 | 教程、完整实现原理、临时设计状态。 |
| `docs/internal/` | 编译器和运行时的详细设计与协议说明 | 面向使用者的语言和 CLI 规范。 |
| `docs/public/` | IDL、CLI 和投影的公开使用规格 | 内部生命周期、缓存和依赖约束。 |
| `test/` | 生成、编译、链接和运行回归 | 使用教程。 |
| `cookbook/` | 可运行的公开能力示例 | 负向语义和内部回归的唯一证据。 |

## 全局边界

- 语言语义、目标投影、ABI 和平台桥必须保持所有权分离；否则单一目标的规则会污染共享语义。
- 编译器与运行时共同定义 ABI；修改任一侧时必须核对另一侧，否则生成代码与运行时会不匹配。
- 生成产物只用于验证，不是规范来源；设计事实必须落在源码或内部设计文档。
- 知识文件只保留稳定边界；完整数据结构和模板协议下沉到 `docs/internal/`。

## 修改前检查

| 问题 | 决策 |
| --- | --- |
| 改动属于语言、IR、后端、ABI、C++ 投影还是平台桥？ | 先确定唯一所有者，再检查相邻边界。 |
| 是否同时改变编译器生成和运行时消费？ | 必须验证两侧契约一致。 |
| 内容是修改约束还是实现说明？ | 前者写知识文件，后者写内部设计文档。 |

## 代码和测试

| 主题 | 锚点 |
| --- | --- |
| 编译器 | `compiler/taihe/` |
| 运行时 | `runtime/include/taihe/`, `runtime/src/` |
| 标准声明 | `stdlib/` |
| 内部设计 | `docs/internal/compiler/`, `docs/internal/runtime/` |
| 验证资产 | `compiler/tests/`, `test/`, `cookbook/` |