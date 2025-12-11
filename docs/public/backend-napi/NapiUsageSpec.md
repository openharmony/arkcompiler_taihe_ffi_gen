# Taihe 工具支持生成 Napi 桥接代码规格文档
# 概述
Taihe 工具支持生成 Napi桥接代码，支持在 C++ 和 ArkTS 之间建立类型安全的接口。本规范定义了 Taihe 支持 Napi 代码生成的语法规范。

# 规格

## 数据类型

- **基本类型**：整数类型、浮点类型、布尔值、字符串
- **容器类型**：Array, ArrayBuffer, TypedArray, Map, Record
- **空**：null, undefined, optional
- **常量和值**：const, enum
- **特殊类型**：bigint, object, callback

## 面向对象

- **面向对象类型**：interface, class, attribute

## 命名空间

- **命名空间类型**： import, namespace

## 运行时

- 异步
- 异常处理

## 逃逸通道
- 支持 Napi 混用
- 支持 ArkTS-Dyn 混用

# 约束

- 只支持静态类型，不支持泛型，typeof，多态，duck typing （动态弱类型语言，无法精确判断类型，无法在 C++ 中映射）
- 只支持接口语义的面向对象能力，不支持重载
- union 只支持区分 字符串、number、布尔值、Array、Map、undefined、null，受语言特性限制无法区分自定义类型。
