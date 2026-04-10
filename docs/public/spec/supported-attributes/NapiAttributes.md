# Taihe IDL napi 注解全集

本文档中仅包含 NAPI 后端特有的注解，通用注解请参考 [Taihe IDL ArkTs注解全集](./ArkTSAttributes.md)。

## 全局注解

- `@!lib("{so_file}")`：表示当前生成的 ts 文件会从指定的 so 文件中寻找 C++ 实现。

- `@!dts_inject("""...""")`：表示将一段代码注入到当前 Taihe 文件所对应的声明文件的 namespace 中。

- `@!dts_inject_into_module("""...""")`：表示将一段代码注入到当前 Taihe 文件所对应的声明文件的 namespace 所在的 module 头部。

- `@!ts_inject("""...""")`：表示将一段代码注入到当前 Taihe 文件所对应的实现文件的 namespace 中。

- `@!ts_inject_into_module("""...""")`：表示将一段代码注入到当前 Taihe 文件所对应的实现文件的 namespace 所在的 module 头部。

## 声明注解

- `@!dts_inject_into_class("""...""")`：将一段代码注入到生成的声明文件的 class 中。可加在 Taihe struct 和 interface 上。

- `@!dts_inject_into_interface("""...""")`：将一段代码注入到生成的声明文件的 interface 中。可加在 Taihe struct 和 interface 上。

- `@!ts_inject_into_class("""...""")`：将一段代码注入到实现的声明文件的 class 中。可加在 Taihe struct 和 interface 上。

- `@!ts_inject_into_interface("""...""")`：将一段代码注入到实现的声明文件的 interface 中。可加在 Taihe struct 和 interface 上。

## 类型注解

- `@dts_type("MyType")`：将一个 Opaque 的实际类型设置为具体的类型 `MyType`。

## 函数/方法注解

- `@constructor("ClassName")`：将一个全局函数在用户侧绑定设置为类 `ClassName` 的构造器。
