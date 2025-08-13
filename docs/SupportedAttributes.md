# Taihe IDL 注解全集

*注：当前本文档中的注解同时包括 Taihe 在所有后端共用的注解和仅针对 ArkTS 1.2 及 ANI 后端特有的注解且未作拆分。后续会进行拆分。*

## 全局注解

- `@namespace("@ohos.abc.xyz", "ns1.ns2.ns3")`：该注解作用于整个 Taihe 文件，作用一是让该文件生成 ets 代码都在 namespace 内；作用二是修改文件名，Taihe 文件不允许使用 @。

- `@sts_inject("""...""")`：注入功能，将一段 ets 代码注入到当前 Taihe 文件所对应的 ets namespace 中。

- `@sts_inject_into_module("""...""")`：注入功能，将一段 ets 代码注入到当前 Taihe 文件所对应的 ets namespace 所在的 module 头部。

## 声明注解

- `@class`：使用此注解将在 Taihe 中声明的 interface 或 struct 在 TS 中投影为 class，如果不使用此注解则默认会被投影为 TS 中的 interface。

- `@sts_inject_into_class("""...""")`：将一段 ets 代码注入到生成的 ets 的 class 中。可加在 Taihe struct 和 interface 上。

- `@sts_inject_into_interface("""...""")`：将一段 ets 代码注入到生成的 ets 的 interface 中。可加在 Taihe struct 和 interface 上。

- `@sts_export_default`：ets 特有语法，将导出的某个目标指定为 default。可加在 Taihe 文件上（表示其所对应的 namespace 为默认导出），也可加在 Taihe enum/union/struct/interface 等声明上（表示其所对应的 ets 目标为默认导出）。

- `@const`：加在 Taihe enum 上，表示该 enum 在 ets 侧被投影为若干个常量，而不是一个 enum 类型。

- `@extends`：加在 struct field 上，用于以组合的方式实现纯数据类的继承。

- `@readonly`：设置 struct 中某个属性为只读属性。

- `@null`：用于将 union 里的某个无类型属性设置为 null 类型。

- `@undefined`：用于将 union 里的某个无类型属性设置为 undefined 类型。

- `@optional`：可加在函数参数或 struct field 上，表示该参数/属性为可选（`a?: T`）。

- `@sts_this`：在类中适用，获得与 Taihe 对象相绑定的 ArkTS 类的 `ani_object`。

## 类型注解

- `@bigint`：将一个 array 绑定到 ets 的 bigint。

- `@arraybuffer`：将一个 array 绑定到 ets 的 arraybuffer。

- `@typedarray`：将一个 array 绑定到 ets 的 typedarray。

- `@fixedarray`：将一个 array 绑定到 ets 的 fixedarray。

- `@record`：将一个 map 绑定到 ets 的 record。

- `@sts_type("MyType")`：将一个 Opaque 的实际类型设置为一个具体的 ets 类型。

## 函数/方法注解

- `@rename("newName")`：修改 ets 侧绑定的函数名。

- `@static("ClassName")`：加在全局函数上，表示其在 ets 侧绑定的函数为静态函数。

- `@constructor("ClassName")`：将一个函数的 ets 绑定设置为某个类的构造器。

- `@get("propertyName")`：将一个函数设置为某个属性/变量的 get 方法。

- `@set("propertyName")`：将一个函数设置为某个属性/变量的 set 方法。

- `@async`：生成一个 ets 侧异步函数绑定。

- `@promise`：生成一个 ets 侧异步函数绑定。

- `@static_overload("overloadedName")`：将一个函数设置为 ets 侧的 java like 重载函数。
