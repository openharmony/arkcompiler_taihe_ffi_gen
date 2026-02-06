# Taihe IDL ArkTS 注解全集

*本文档中以 `@!` 开头的表示该注解通常被写作[内联注解](../IdlReference.md#内联注解)，其余以 `@` 开头的表示该注解通常被写作[前缀注解](../IdlReference.md#前缀注解)。*

## 全局注解

- `@!namespace("@ohos.abc.xyz", "ns1.ns2.ns3")`：该注解作用于整个 Taihe 文件。其中第一个参数表示该 Taihe 文件所对应的 module 名称，第二个参数可选，表示该 Taihe 文件所对应于该 module 下的 namespace 名称，若不指定则默认表示该 Taihe 文件对应该 module 的根作用域。如果不使用该注解，则默认该 Taihe 文件所对应 module 名称为 Taihe 文件的包名，namespace 名称为根作用域。

## 声明注解

- `@class`：使用此注解将在 Taihe 中声明的 interface 或 struct 在用户侧中投影为 class，如果不使用此注解则默认会被投影为用户侧中的 interface。

- `@const`：加在 Taihe enum 上，表示该 enum 在用户侧被投影为若干个常量，而不是一个 enum 类型。

- `@extends`：加在 struct field 上，用于以组合的方式实现纯数据类的继承。

- `@readonly`：设置 struct 中某个 field 为只读。

## 类型注解

- `@undefined`：添加在 Taihe `unit` 类型上，表示该 `unit` 类型在用户侧被投影为 `undefined`，而非默认的 `null`。

- `@null`：添加在 Taihe `unit` 类型上，表示该 `unit` 类型在用户侧被投影为 `null`，该注解实际上与不添加任何注解的效果相同，仅用于明确标识该 `unit` 类型的语义。

- `@bigint`：将一个 Taihe `Array<u64>` 在用户侧中投影为 `BigInt`。（使用可变长小端序补码编码）

- `@arraybuffer`：将一个 Taihe `Array<u8>` 在用户侧中投影为 `ArrayBuffer`。

- `@typedarray`：将一个 Taihe `Array` 在用户侧中投影为 `TypedArray`。（仅支持 `Array<u8>`, `Array<u16>`, `Array<u32>`, `Array<u64>`, `Array<i8>`, `Array<i16>`, `Array<i32>`, `Array<i64>`, `Array<f32>`, `Array<f64>`）

- `@record`：将一个 Taihe `Map` 在用户侧中投影为 `Record`。

## 函数/方法注解

- `@static("ClassName")`：加在全局函数上，表示其在用户侧绑定的函数为静态函数。该注解**可以**与 `@rename` 一起使用。

- `@ctor("ClassName")`：加在全局函数上，表示其在用户侧绑定的函数为某个类的构造器。该注解**不能**与 `@rename` 一起使用。

- `@get("propertyName")`：将一个方法设置为某个属性/变量的 get 方法。

- `@set("propertyName")`：将一个方法设置为某个属性/变量的 set 方法。
