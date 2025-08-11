# Taihe 能力全集

## Taihe 类型能力

- **整型**
  - 无符号：`u8`, `u16`, `u32`, `u64`  注：ArkTS 1.2 不支持无符号类型
  - 有符号：`i8`, `i16`, `i32`, `i64`

- **浮点型**
  - `f32`, `f64`

- **布尔型**
  - `bool`

- **字符串类型**
  - `String`

- **枚举类型**
  - `enum`

- **联合类型**
  - `union`

- **容器类型**
  - `Optional<T>`：可选类型，表示值可能存在或不存在，支持任意类型 `T`。
  - `Array<T>`：长度在创建后即不可变数组类型，支持任意成员类型 `T`。
  - `Map<K, V>`：映射类型，支持键值对，其中键类型为 `K`，值类型为 `V`。
  - `Set<T>`：集合类型，支持任意成员类型 `T`。
  - `Vector<T>`：可动态变长的数组类型，支持任意成员类型 `T`。

- **函数闭包类型**
  - `(arg1: Type1, arg2: Type2, ...) => ReturnType`：表示函数类型，支持任意数量的参数和一个返回值。

- **外部类型**
  - `Opaque`

## ArkTS 1.2 注解能力

`@namespace`；该注解作用于整个 Taihe 文件，作用一是让该文件生成 ets 代码都在 namespace 内；作用二是修改文件名，Taihe 文件不允许使用 @。

`@sts_export_default`：ets 特有语法，将导出的某个目标指定为 default。

`@sts_inject`：注入功能，将一段ets代码注入到生成的 ets 文件中。

`@sts_inject_into_module`：注入功能，将一段 ets 代码注入到生成的 ets 的 module 中。

`@sts_inject_into_class`：注入功能，将一段 ets 代码注入到生成的 ets 的 class 中。

`@sts_inject_into_interface`：注入功能，将一段 ets 代码注入到生成的 ets 的 interface 中。

`@class`：原本 taihe 代码会对一个 taihe 的 interface 生成一个 interface 和一个实现的 class，现在直接生成为 class。

`@const`：在 ets 侧生成常量值。

`@extends`：用于以组合的方式实现纯数据类的继承。

`@readonly`：设置某个属性为只读属性。

`@null`：用于将union里的某个属性设置为 null 类型。

`@undefined`：用于将union里的某个属性设置为 undefined 类型。

`@optional`：将一个类型的 ets 绑定设置为 `?` 类型

`@sts_this`：在类中适用，获得与 Taihe 对象相绑定的 ArkTS 类的 `ani_object`。

`@bigint`：将一个 array 绑定到 ets 的 bigint。

`@arraybuffer`：将一个 array 绑定到 ets 的 arraybuffer。

`@typedarray`：将一个 array 绑定到 ets 的 typedarray。

`@fixedarray`：将一个 array 绑定到 ets 的 fixedarray。

`@record`：将一个 map 绑定到 ets 的 record。

`@sts_type`：将一个 Opaque 的实际类型设置为一个具体的 ets 类型。

`@rename`：修改 ets 侧绑定的函数名。

`@static`：修改 ets 侧绑定的函数为静态函数。

`@constructor`：将一个函数的 ets 绑定设置为某个类的构造器。

`@get`：将一个函数设置为某个属性/变量的 get 方法。

`@set`：将一个函数设置为某个属性/变量的 set 方法。

`@async`：生成一个 ets 侧异步函数绑定

`@promise`：生成一个 ets 侧异步函数绑定

`@static_overload`：将一个函数设置为 ets 侧的 java like 重载函数
