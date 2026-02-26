# 特性速查表

本页面提供 Taihe 各项特性的快速索引，方便你快速找到所需功能的文档。

---

## 基础类型与数据结构

| 特性 | 说明 | 文档 |
|------|------|------|
| 基础类型 | `i32`, `f64`, `String`, `bool` 等 | [基础能力](../basic_abilities/README.md) |
| 容器类型 | `Array`, `Optional`, `Vector`, `Map`, `Set` | [基础能力](../basic_abilities/README.md) |
| `struct` | 纯数据结构体 | [Struct 与 Tuple](../struct_tuple/README.md) |
| `enum` | 枚举类型 | [Enum 与 Union](../enum_union/README.md) |
| `union` | 联合类型 | [Enum 与 Union](../enum_union/README.md) |
| `interface` | 接口定义 | [Interface](../interface/README.md) |
| `Optional` | 可选类型 | [Optional](../optional/README.md) |

## 模块与继承

| 特性 | 说明 | 文档 |
|------|------|------|
| `import` | 导入其他模块 | [Import](../import/README.md) |
| 继承 | 接口继承 | [继承](../inherit/README.md) |
| 多继承 | 实现多个接口 | [多继承](../multiple_inherit/README.md) |

## 函数与回调

| 特性 | 说明 | 文档 |
|------|------|------|
| Callback | 回调函数 | [Callback](../callback/README.md) |
| Callback 比较 | 判断回调是否相等 | [Callback 比较](../callback_compare/README.md) |
| `Opaque` | 外部对象 | [External Object](../external_obj/README.md) |

---

## 注解参考

> **💡 提示**：阅读下面的章节前，建议先了解 [注解语法](../async/README.md#注解语法)。

### 类型相关注解

| 注解 | 说明 | 文档 |
|------|------|------|
| `@namespace` | 指定 ArkTS 命名空间 | [Namespace](../namespace/README.md) |
| `@arraybuffer` | 映射为 ArrayBuffer | [ArrayBuffer](../arraybuffer/README.md) |
| `@typedarray` | 映射为 TypedArray | [TypedArray](../typedarray/README.md) |
| `@fixedarray` | 映射为 FixedArray | [TypedArray](../typedarray/README.md) |
| `@bigint` | 映射为 BigInt | [BigInt](../bigint/README.md) |
| `@record` | 映射为 Record | [Optional](../optional/README.md) |
| `@null` / `@undefined` | 声明可空类型 | [Null 与 Undefined](../null_undefined/README.md) |
| `@literal("str")` | unit 映射为字符串字面量 | [ANI 注解](../../docs/public/spec/supported-attributes/AniAttributes.md) |

### 接口与类相关注解

| 注解 | 说明 | 文档 |
|------|------|------|
| `@class` | Interface 映射为 class | [Override](../class/README.md) |
| `@ctor` | 声明构造函数 | [Override](../class/README.md) |
| `@static` | 声明静态函数 | [Override](../class/README.md) |
| `@get` / `@set` | 声明 getter/setter | [属性](../property/README.md) |
| `@readonly` | 只读字段 | [属性](../property/README.md) |
| `@tuple` | Struct 投影为元组 | [Struct 与 Tuple](../struct_tuple/README.md) |
| `@extends` | 纯数据类继承 | [Struct 继承](../struct_extends/README.md) |
| `@const` | 枚举常量化 | [Enum 与 Union](../enum_union/README.md) |

### 字段与参数相关注解

| 注解 | 说明 | 文档 |
|------|------|------|
| `@optional` | 可选参数/字段 | [Optional](../optional/README.md) |
| `@sts_this` | 隐式传入 this | [ANI 注解](../../docs/public/spec/supported-attributes/AniAttributes.md) |
| `@sts_last` | 重复上一个参数 | [ANI 注解](../../docs/public/spec/supported-attributes/AniAttributes.md) |
| `@sts_fill("expr")` | 填充表达式 | [ANI 注解](../../docs/public/spec/supported-attributes/AniAttributes.md) |

### 函数相关注解

| 注解 | 说明 | 文档 |
|------|------|------|
| `@async` | 异步函数 | [异步](../async/README.md) |
| `@promise` | Promise 函数 | [异步](../async/README.md) |
| `@rename` | 重命名函数 | [重命名](../rename_example/README.md) |
| `@gen_async` ⚠️ | 生成异步版本（已废弃） | [异步](../async/README.md) |
| `@gen_promise` ⚠️ | 生成 Promise 版本（已废弃） | [异步](../async/README.md) |
| `@on_off` | 事件监听 | [On/Off](../on_off/README.md) |

### 代码注入注解

| 注解 | 说明 | 文档 |
|------|------|------|
| `@sts_inject` | 注入 ArkTS 代码 | [External Object](../external_obj/README.md) |
| `@!sts_inject_into_class` | 注入到 class | [Essential](../essential/README.md) |
| `@!sts_inject_into_interface` | 注入到 interface | [Essential](../essential/README.md) |

---

## 完整参考

- [Essential Sheet](../essential/README.md) - Taihe 核心概念速览
- [Taihe IDL 语言规范](../../docs/public/spec/IdlReference.md) - 完整语法参考
- [ANI 注解全集](../../docs/public/spec/supported-attributes/AniAttributes.md) - 所有 ANI 注解

- [如何在 Taihe 中实现多继承](../multiple_inherit/README.md)