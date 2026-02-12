# Taihe IDL ani 注解全集

本文档中仅包含 ANI 后端特有的注解，此外，[ArkTS 后端通用的注解](ArkTSAttributes.md) 也都适用于 ANI 后端。

## 全局注解

- `@!sts_inject("""...""")`：表示将一段 ets 代码注入到当前 Taihe 文件所对应的 ets namespace 中。

- `@!sts_inject_into_module("""...""")`：表示将一段 ets 代码注入到当前 Taihe 文件所对应的 ets namespace 所在的 module 头部。

## 声明注解

- `@!sts_inject_into_class("""...""")`：将一段 ets 代码注入到生成的 ets 的 class 中。可加在 Taihe struct 和 interface 上。

- `@!sts_inject_into_interface("""...""")`：将一段 ets 代码注入到生成的 ets 的 interface 中。可加在 Taihe struct 和 interface 上。

- `@!sts_export_default/@sts_export_default`：ets 特有语法，将导出的某个目标指定为 default。可加在 Taihe 文件上（表示其所对应的 namespace 为默认导出），也可加在 Taihe enum/union/struct/interface 等声明上（表示其所对应的 ets 声明为默认导出）。

- `@optional`：可加在函数参数或 struct field 上，表示该参数/属性为可选（`a?: T`）。需要注意的是，该参数/属性类型必须同时为 Optional 类型，例如 `@optional a: Optional<T>`。

- `@sts_this`：用在函数或方法的某个参数上，使用了该注解的参数在 ets 侧投影的对应函数中不会出现，调用时会隐式将 `this` 传入该参数位置传给实现侧。通常用于因为某些原因需要以其他类型（如 `Opaque`）捕获上层 `this` 对象的场景。

- `@sts_last`：用在函数或方法的某个参数上，使用了该注解的参数在 ets 侧投影的对应函数中不会出现，调用时会隐式将该参数的上一个参数重复传入该参数位置传给实现侧。例如，若某个函数定义为 `func(a: A, @sts_last b: B): void`，则在 ets 侧投影的函数形式为 `func(a: A): void`，调用时下层会同时收到 `a` 作为 `a` 和 `b` 两个参数的值传入实现侧。

- `@sts_fill("expression")`：用在函数或方法的某个参数上，使用了该注解的参数在 ets 侧投影的对应函数中不会出现，调用时会隐式将 `expression` 传入该参数位置传给实现侧。`expression` 可以使用前面参数的名字作为表达式的一部分。例如，若某个函数定义为 `func(a: A, @sts_fill("a.toString()") b: string): void`，则在 ets 侧投影的函数形式为 `func(a: A): void`，调用时下层会同时收到 `a` 作为 `a` 参数的值，以及 `a.toString()` 作为 `b` 参数的值传入实现侧。

## 类型注解

- `@literal("literalString")`：将一个 Taihe `unit` 类型在用户侧中投影为一个字面量字符串类型，且该字面量字符串的值为 `literalString`。例如，`a: @literal("foo") unit` 将在用户侧被投影为 `a: "foo"`。

- `@fixedarray`：将 Taihe `Array<T>` 在用户侧中投影为 `fixedarray<T>`。

- `@sts_type("MyType")`：将一个 `Opaque` 类型在 ArkTS 侧投影为 `MyType` 类型。如果 `MyType` 不在当前编译单元中定义，用户需要通过通过 `@!sts_inject_into_module` 注入相应的导入语句来引入 `MyType` 的定义。

## 函数/方法注解

- `@rename("newName")`：修改用户侧对应投影函数/方法的名字。

- `@overload("newName")`：**该注解计划废弃，禁止在新的 Taihe 文件中继续使用该注解，请使用更通用的 `@rename` 注解替代。**修改用户侧对应投影函数/方法的名字，并且允许多个 Taihe 函数/方法投影到同一个名字上形成重载。

- `@constructor("ClassName")`：将一个全局函数在用户侧绑定设置为某个类的**命名**构造器。该注解**可以**与 `@rename` 一起使用。

- `@async`：将一个返回 `T` 类型同步函数封装为接受 `AsyncCallback<T>` 的异步函数。（`type AsyncCallback<T> = (error: BusinessError | null, data: T | undefined) => void;`）

- `@promise`：将一个返回 `T` 的函数封装为返回 `Promise<T>` 的异步函数。

- `@gen_async("asyncName")`：在保留同步函数的同时，额外生成一个名称为 `asyncName` 的，接受 `AsyncCallback<T>` 的异步函数。参数 `asyncName` 可省略，当省略时，默认生成的异步函数名称为 `原函数名.rstrip("Sync")`。例如，若原函数名为 `fooSync`，则默认生成的异步函数名为 `foo`。**该注解计划废弃，禁止在新的 Taihe 文件中继续使用该注解，建议直接使用 `@async` 分别声明同步和异步函数。**

- `@gen_promise("promiseName")`：在保留原函数的同时，额外生成一个名称为 `promiseName` 的，返回 `Promise<T>` 的异步函数。参数 `promiseName` 可省略，当省略时，默认生成的 Promise 函数名称为 `原函数名.rstrip("Sync")`。例如，若原函数名为 `fooSync`，则默认生成的 Promise 函数名为 `foo`。**该注解计划废弃，禁止在新的 Taihe 文件中继续使用该注解，建议直接使用 `@promise` 分别声明同步和异步函数。**

- `@on_off("typeName", name="funcName")`：如果原始函数形式为 `foo(a: int, b: int): void`，则使用该注解后会变形成 `funcName(type: "typeName", a: int, b: int): void`。`typeName` 和 `funcName` 均可省略，当省略 `funcName` 时，要求函数以 `on` 或 `off` 开头，并以 `on` 或 `off` 作为生成函数的名称。当省略 `typeName` 时，会使用 `原函数名.lstrip(funcName)` 作为 `typeName`。例如，若原函数名为 `onEvent(a: int): void`，则使用 `@on_off` 注解并省略 `funcName` 和 `typeName` 后生成的函数形式为 `on(type: "Event", a: int): void`。
