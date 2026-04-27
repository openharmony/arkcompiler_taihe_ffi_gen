# Taihe IDL ANI 注解全集

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

- `@fixedarray`：将 Taihe `Array<T>` 在用户侧中投影为 `FixedArray<T>`。

- `@valuearray`：将 Taihe `Array<T>` 在用户侧中投影为 `ValueArray<T>`。

- `@sts_type("MyType")`：将一个 `Opaque` 类型在 ArkTS 侧投影为 `MyType` 类型。如果 `MyType` 不在当前编译单元中定义，用户需要通过通过 `@!sts_inject_into_module` 注入相应的导入语句来引入 `MyType` 的定义。

## 函数/

- `@constructor("ClassName")`：将一个全局函数在用户侧绑定设置为某个类的**命名**构造器。该注解**可以**与 `@rename` 一起使用。

- `@ctor("ClassName")`：加在全局函数上，表示其在用户侧绑定的函数为某个类的构造器。该注解**不能**与 `@rename` 一起使用。
