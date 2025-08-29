# Taihe IDL 注解全集

*注：当前本文档中的注解同时包括 Taihe 在所有后端共用的注解和仅针对 ArkTS 1.2 及 ANI 后端特有的注解且未作拆分。后续会进行拆分。*

*本文档中以 `@!` 开头的表示该注解通常被写作[内联注解](./IdlReference.md#内联注解)，其余以 `@` 开头的表示该注解通常被写作[前缀注解](./IdlReference.md#前缀注解)。*

## 全局注解

- `@!namespace("@ohos.abc.xyz", "ns1.ns2.ns3")`：该注解作用于整个 Taihe 文件。其中第一个参数表示该 Taihe 文件所对应的 ets module 名称，第二个参数可选，表示该 Taihe 文件所对应于该 ets module 下的 namespace 名称（若不指定则表示该 Taihe 文件对应该 ets module 的根作用域）。如果不使用该注解，则默认该 Taihe 文件所对应的 ets module 名称为 Taihe 文件的包名，namespace 名称为根作用域。

- `@!sts_inject("""...""")`：表示将一段 ets 代码注入到当前 Taihe 文件所对应的 ets namespace 中。

- `@!sts_inject_into_module("""...""")`：表示将一段 ets 代码注入到当前 Taihe 文件所对应的 ets namespace 所在的 module 头部。

## 声明注解

- `@!sts_inject_into_class("""...""")`：将一段 ets 代码注入到生成的 ets 的 class 中。可加在 Taihe struct 和 interface 上。

- `@!sts_inject_into_interface("""...""")`：将一段 ets 代码注入到生成的 ets 的 interface 中。可加在 Taihe struct 和 interface 上。

- `@!sts_export_default`：ets 特有语法，将导出的某个目标指定为 default。可加在 Taihe 文件上（表示其所对应的 namespace 为默认导出），也可加在 Taihe enum/union/struct/interface 等声明上（表示其所对应的 ets 声明为默认导出）。

- `@class`：使用此注解将在 Taihe 中声明的 interface 或 struct 在 TS 中投影为 class，如果不使用此注解则默认会被投影为 TS 中的 interface。

- `@const`：加在 Taihe enum 上，表示该 enum 在 ets 侧被投影为若干个常量，而不是一个 enum 类型。

- `@extends`：加在 struct field 上，用于以组合的方式实现纯数据类的继承。

- `@readonly`：设置 struct 中某个 field 为只读。

- `@optional`：可加在函数参数或 struct field 上，表示该参数/属性为可选（`a?: T`）。需要注意的是，该参数/属性类型必须同时为 Optional 类型，例如 `@optional a: Optional<T>`。

- `@sts_this`：加在函数参数上，表示该参数在 ets 侧的函数投影中被省略，native 侧相应参数被自动填充 ets 侧的 `this`。

## 类型注解

- `@undefined`：添加在 Taihe unit 类型上，表示该 unit 类型在 ets 侧被投影为 undefined。

- `@bigint`：将一个 Taihe Array 在 ets 中投影为 BigInt。（使用可变长小端序补码编码，仅支持 `Array<u64>`）

- `@arraybuffer`：将一个 Taihe Array 在 ets 中投影为 ArrayBuffer。（仅支持 `Array<u8>`）

- `@typedarray`：将一个 Taihe Array 在 ets 中投影为 TypedArray。（仅支持 `Array<u8>`, `Array<u16>`, `Array<u32>`, `Array<u64>`, `Array<i8>`, `Array<i16>`, `Array<i32>`, `Array<i64>`, `Array<f32>`, `Array<f64>`）

- `@fixedarray`：将一个 Taihe Array 在 ets 中投影为 fixedarray。

- `@record`：将一个 Taihe Map 在 ets 中投影为 Record。

- `@sts_type("MyType")`：将一个 Opaque 的实际类型设置为一个具体的 ets 类型。

## 函数/方法注解

- `@rename("newName")`：修改 ets 侧对应投影函数/方法的名字。

- `@static("ClassName")`：加在全局函数上，表示其在 ets 侧绑定的函数为静态函数。

- `@constructor("ClassName")`：将一个全局函数在 ets 侧绑定设置为某个类的构造器。

- `@get("propertyName")`：将一个方法设置为某个属性/变量的 get 方法。

- `@set("propertyName")`：将一个方法设置为某个属性/变量的 set 方法。

- `@async`：将一个返回 `T` 类型同步函数封装为接受 `AsyncCallback<T>` 的异步函数。（`type AsyncCallback<T> = (error: BusinessError | null, data: T | undefined) => void;`）

- `@promise`：将一个返回 `Promise<T>` 的函数封装为返回 `Promise<T>` 的异步函数。

- `@static_overload("overloadedName")`：将一个函数设置为 ets 侧的 java like 重载函数。（`overload overloadedName { funcA, funcB, ... }`）
