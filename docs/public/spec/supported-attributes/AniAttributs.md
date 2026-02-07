# Taihe IDL ani 注解全集

本文档中仅包含 ANI 后端特有的注解，通用注解请参考 [Taihe IDL 公用注解全集](./CommonAttributes.md)。

## 全局注解

- `@!sts_inject("""...""")`：表示将一段 ets 代码注入到当前 Taihe 文件所对应的 ets namespace 中。

- `@!sts_inject_into_module("""...""")`：表示将一段 ets 代码注入到当前 Taihe 文件所对应的 ets namespace 所在的 module 头部。

## 声明注解

- `@!sts_inject_into_class("""...""")`：将一段 ets 代码注入到生成的 ets 的 class 中。可加在 Taihe struct 和 interface 上。

- `@!sts_inject_into_interface("""...""")`：将一段 ets 代码注入到生成的 ets 的 interface 中。可加在 Taihe struct 和 interface 上。

- `@!sts_export_default`：ets 特有语法，将导出的某个目标指定为 default。可加在 Taihe 文件上（表示其所对应的 namespace 为默认导出），也可加在 Taihe enum/union/struct/interface 等声明上（表示其所对应的 ets 声明为默认导出）。

- `@optional`：可加在函数参数或 struct field 上，表示该参数/属性为可选（`a?: T`）。需要注意的是，该参数/属性类型必须同时为 Optional 类型，例如 `@optional a: Optional<T>`。

## 类型注解

- `@fixedarray`：将一个 Taihe Array 在用户侧中投影为 fixedarray。

- `@sts_type("MyType")`：将一个 Opaque 的实际类型设置为一个具体的 ets 类型。

## 函数/方法注解

- `@rename("newName")`：修改用户侧对应投影函数/方法的名字。

- `@constructor("ClassName")`：将一个全局函数在用户侧绑定设置为某个类的构造器。

- `@async`：将一个返回 `T` 类型同步函数封装为接受 `AsyncCallback<T>` 的异步函数。（`type AsyncCallback<T> = (error: BusinessError | null, data: T | undefined) => void;`）

- `@promise`：将一个返回 `Promise<T>` 的函数封装为返回 `Promise<T>` 的异步函数。
