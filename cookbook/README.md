# Taihe Cookbook

本 Cookbook 提供了一系列由浅入深的实践教程，帮助你快速掌握 Taihe 的各种特性和最佳实践。

## 前置条件

在开始之前，请确保你已经：

1. 完成 [开发环境搭建](../docs/internal/DevSetup.md)
2. 了解 [Taihe 基本概念](../docs/public/Overview.md)
3. 熟悉 [命令行工具使用](../docs/public/CliReference.md)

## 如何使用本 Cookbook

每个教程都遵循相同的结构：

1. **目标说明** - 本教程要实现的功能
2. **第一步：编写 IDL** - 在 `.taihe` 文件中声明接口
3. **第二步：实现 C++** - 编写 C++ 实现代码
4. **第三步：测试验证** - 使用 `taihe-tryit` 编译运行

建议按顺序学习第一章的内容，后续章节可根据需要选择性阅读。

---

## 第一章：基础与绑定

从零开始学习 Taihe 的核心概念。

| 教程 | 说明 |
|------|------|
| [Hello World](hello_world/README.md) | 将 C++ 函数绑定到 ArkTS，最简单的入门示例 |
| [绑定机制](binding/README.md) | 深入理解 Taihe 的方法绑定原理 |
| [基础能力](basic_abilities/README.md) | 掌握基础类型、容器类型的使用 |

## 第二章：接口与类型

学习自定义类型和接口的声明与使用。

| 教程 | 说明 |
|------|------|
| [Interface 接口](interface/README.md) | 定义和实现纯方法类 |
| [Import 导入](import/README.md) | 模块化：导入其他 Taihe IDL 文件 |
| [Enum 与 Union](enum_union/README.md) | 枚举类型和联合类型的使用 |
| [继承](inherit/README.md) | 接口继承与 `@get`/`@set` 属性 |
| [Optional 可选类型](optional/README.md) | 可选参数和可空类型 |

## 第三章：进阶与扩展

掌握高级特性，应对复杂场景。

| 教程 | 说明 |
|------|------|
| [异步 async/promise](async/README.md) | 异步函数与 Promise 支持 |
| [Callback 回调](callback/README.md) | 函数作为参数传递 |
| [Opaque 外部对象](external_obj/README.md) | 处理外部语言对象 |
| [Override 覆写](override/README.md) | `@class`、`@ctor`、`@static` |
| [ArrayBuffer](arraybuffer/README.md) | 二进制数据处理 |
| [TypedArray](typedarray/README.md) | 类型化数组 |
| [BigInt](bigint/README.md) | 大整数支持 |
| [On/Off 事件](on_off/README.md) | 事件订阅与取消 |
| [Struct 继承](struct_extends/README.md) | 纯数据类型的继承 |
| [Class 继承](class_extend/README.md) | Class 的继承实现 |
| [多继承](multiple_inherit/README.md) | 接口多继承 |
| [多态](polymorphism/README.md) | 多态作为入参出参 |
| [GetInner](unwrap_obj/README.md) | 获取 Taihe 绑定的实现类 |
| [Null 与 Undefined](null_undefined/README.md) | 空值类型处理 |
| [Callback 比较](callback_compare/README.md) | 回调对象的比较判断 |
| [函数重命名](rename_example/README.md) | `@rename` 注解的使用 |

## 附录

| 资源 | 说明 |
|------|------|
| [Essential Sheet](essential/README.md) | Taihe 核心概念速览 |
| [特性速查表](quick_ref/README.md) | 按功能分类的快速索引 |
| [C++ 使用指南](taihe_cpp/README.md) | Taihe C++ 运行时详解 |

---

## 更多资源

- [Taihe IDL 语言规范](../docs/public/spec/IdlReference.md)
- [ANI 注解参考](../docs/public/spec/supported-attributes/AniAttributes.md)
- [C++ 生成代码解析](../docs/public/backend-cpp/CppGeneratedCode.md)
