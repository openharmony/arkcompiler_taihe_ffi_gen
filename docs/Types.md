# 太和数据类型

本文介绍太和支持的数据类型。

## 基础类型

即基本的数值类型，不涉及引用计数管理。

| 类型 | C++ 侧投影 | C++ 侧投影（作为参数时） |
|--------|------------|------------|
| `i8`   | `int8_t`   | `int8_t`   |
| `i16`  | `int16_t`  | `int16_t`  |
| `i32`  | `int32_t`  | `int32_t`  |
| `i64`  | `int64_t`  | `int64_t`  |
| `u8`   | `uint8_t`  | `uint8_t`  |
| `u16`  | `uint16_t` | `uint16_t` |
| `u32`  | `uint32_t` | `uint32_t` |
| `u64`  | `uint64_t` | `uint64_t` |
| `f32`  | `float`    | `float`    |
| `f64`  | `double`   | `double`   |
| `bool` | `bool`     | `bool`     |

## 容器类型

包括字符串类型、可变长的数组、字典、集合类型，以及函数闭包等。
- 可变性：除 `String` 类型不可变外，其余所有类型均可变并且默认以可变的方式传参。
- 引用计数：其中 `Array<T>`（定长数组）和 `Box<T>`（可空引用）类型表示的是值语义，无引用计数，在 C++ 中拷贝时会同时复制其内部数据。其余类型均通过引用计数进行管理。

| 类型 | C++ 侧投影 | C++ 侧投影（作为参数时） | 引用计数 | 说明 |
|-------------|--------------------|-------------------------|----|----|
| `Array<T>`  | `taihe::array<T>`  | `taihe::array_view<T>`  | 无 | 无引用计数的定长数组类型 |
| `Box<T>`    | `taihe::box<T>`    | `taihe::box_view<T>`    | 无 | 无引用计数的可空引用类型 |
| `String`    | `taihe::string`    | `taihe::string_view`    | 有 | 字符串类型，通过引用计数管理 |
| `Vector<T>` | `taihe::vector<T>` | `taihe::vector_view<T>` | 有 | 通过引用计数管理的可变长数组 |
| `Map<K, V>` | `taihe::map<K, V>` | `taihe::map_view<K, V>` | 有 | 通过引用计数管理的字典类型 |
| `Set<T>`    | `taihe::set<T>`    | `taihe::set_view<T>`    | 有 | 通过引用计数管理的集合类型 |
| `(a: A, b: B) => T` | `taihe::callback<T(A, B)>` | `taihe::callback_view<T(A, B)>` | 有 | 通过引用计数管理的函数闭包 |

# 用户自定义类型

支持自定义结构体、联合体和接口类型。其中，结构体和联合体为值语义，用于表示若干成员的组合或变体，以不可变的方式传参。接口类型通过引用计数管理。

具体的定义和使用方法见 [DSL.md](./DSL.md) 和 [UserDoc.md](./UserDoc.md).

| 类型 | C++ 侧投影 | C++ 侧投影（作为参数时） | 引用计数 |
|---------------|------------------|--------------------------|----|
| `struct S`    | `name::space::S` | `const name::space::S &` | 无 |
| `enum E`      | `name::space::E` | `const name::space::E &` | 无 |
| `interface I` | `name::space::I` | `name::space::weak::I`   | 有 |
