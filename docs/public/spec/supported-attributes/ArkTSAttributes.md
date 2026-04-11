# Taihe IDL ArkTS 注解全集

*本文档中以 `@!` 开头的表示该注解通常被写作[内联注解](../IdlReference.md#内联注解)，其余以 `@` 开头的表示该注解通常被写作[前缀注解](../IdlReference.md#前缀注解)。*

## 全局注解

- `@!namespace("@ohos.abc.xyz", "ns1.ns2.ns3")`：该注解作用于整个 Taihe 文件。其中第一个参数表示该 Taihe 文件所对应的 module 名称，第二个参数可选，表示该 Taihe 文件所对应于该 module 下的 namespace 名称，若不指定则默认表示该 Taihe 文件对应该 module 的根作用域。如果不使用该注解，则默认该 Taihe 文件所对应 module 名称为 Taihe 文件的包名，namespace 名称为根作用域。

## 声明注解

- `@const`：加在 Taihe enum 上，表示该 enum 在用户侧被投影为若干个常量，而不是一个 enum 类型。

- `@class`：使用此注解将在 Taihe 中声明的 interface 或 struct 在用户侧中投影为 class，如果不使用此注解则默认会被投影为用户侧中的 interface。

- `@tuple`：使用此注解将在 Taihe 中声明的 struct 在用户侧中投影为 tuple，而非默认的 interface。

- `@extends`：加在 struct field 上，用于以组合的方式实现纯数据类的继承。

- `@readonly`：设置 struct 中某个 field 为只读。

- `@rename("newName")`：修改用户侧对应投影的名字。该注解可用于 enum/union/struct/interface（修改类型名称）、function/method（修改函数/方法名称）、field（修改属性名称）、parameter（修改参数名称）。

## 类型注解

- `@undefined`：添加在 Taihe `unit` 类型上，表示该 `unit` 类型在用户侧被投影为 `undefined`，而非默认的 `null`。

- `@null`：添加在 Taihe `unit` 类型上，表示该 `unit` 类型在用户侧被投影为 `null`，该注解实际上与不添加任何注解的效果相同，仅用于明确标识该 `unit` 类型的语义。

- `@literal("literalString")`：将一个 Taihe `unit` 类型在用户侧中投影为一个字面量字符串类型，且该字面量字符串的值为 `literalString`。例如，`a: @literal("foo") unit` 将在用户侧被投影为 `a: "foo"`。

- `@bigint`：将一个 Taihe `Array<u64>` 在用户侧中投影为 `BigInt`。（使用可变长小端序补码编码）

- `@arraybuffer`：将一个 Taihe `Array<u8>` 在用户侧中投影为 `ArrayBuffer`。

- `@typedarray`：将一个 Taihe `Array` 在用户侧中投影为 `TypedArray`。（仅支持 `Array<u8>`, `Array<u16>`, `Array<u32>`, `Array<u64>`, `Array<i8>`, `Array<i16>`, `Array<i32>`, `Array<i64>`, `Array<f32>`, `Array<f64>`）

- `@record`：将一个 Taihe `Map` 在用户侧中投影为 `Record`。

## 函数/方法注解

- `@static("ClassName")`：加在全局函数上，表示其在用户侧绑定的函数为静态函数。该注解**可以**与 `@rename` 一起使用。

- `@get("propertyName")`：将一个方法设置为某个属性/变量的 get 方法。

- `@set("propertyName")`：将一个方法设置为某个属性/变量的 set 方法。

- `@overload("newName")`：**该注解计划废弃，禁止在新的 Taihe 文件中继续使用该注解，请使用更通用的 `@rename` 注解替代。**修改用户侧对应投影函数/方法的名字，并且允许多个 Taihe 函数/方法投影到同一个名字上形成重载。

- `@async`：将一个返回 `T` 类型同步函数封装为接受 `AsyncCallback<T>` 的异步函数。（`type AsyncCallback<T> = (error: BusinessError | null, data: T | undefined) => void;`）

- `@promise`：将一个返回 `T` 的函数封装为返回 `Promise<T>` 的异步函数。

- `@gen_async("asyncName")`：在保留同步函数的同时，额外生成一个名称为 `asyncName` 的，接受 `AsyncCallback<T>` 的异步函数。参数 `asyncName` 可省略，当省略时，默认生成的异步函数名称为 `原函数名.rstrip("Sync")`。例如，若原函数名为 `fooSync`，则默认生成的异步函数名为 `foo`。**该注解计划废弃，禁止在新的 Taihe 文件中继续使用该注解，建议直接使用 `@async` 分别声明同步和异步函数。**

- `@gen_promise("promiseName")`：在保留原函数的同时，额外生成一个名称为 `promiseName` 的，返回 `Promise<T>` 的异步函数。参数 `promiseName` 可省略，当省略时，默认生成的 Promise 函数名称为 `原函数名.rstrip("Sync")`。例如，若原函数名为 `fooSync`，则默认生成的 Promise 函数名为 `foo`。**该注解计划废弃，禁止在新的 Taihe 文件中继续使用该注解，建议直接使用 `@promise` 分别声明同步和异步函数。**

- `@on_off("typeName", name="funcName")`：如果原始函数形式为 `foo(a: int, b: int): void`，则使用该注解后会变形成 `funcName(type: "typeName", a: int, b: int): void`。`typeName` 和 `funcName` 均可省略，当省略 `funcName` 时，要求函数以 `on` 或 `off` 开头，并以 `on` 或 `off` 作为生成函数的名称。当省略 `typeName` 时，会使用 `原函数名.lstrip(funcName)` 作为 `typeName`。例如，若原函数名为 `onEvent(a: int): void`，则使用 `@on_off` 注解并省略 `funcName` 和 `typeName` 后生成的函数形式为 `on(type: "Event", a: int): void`。
