# 太和数据类型

本文介绍太和支持的数据类型。

| 类型 | C++ 侧投影 | C++ 侧投影（作为参数时） | 引用计数 | 说明 |
|---------------|--------------------------|-------------------------------|---|---|
| `i8`          | `int8_t`                 | `int8_t`                      | 无 | / |
| `i16`         | `int16_t`                | `int16_t`                     | 无 | / |
| `i32`         | `int32_t`                | `int32_t`                     | 无 | / |
| `i64`         | `int64_t`                | `int64_t`                     | 无 | / |
| `u8`          | `uint8_t`                | `uint8_t`                     | 无 | / |
| `u16`         | `uint16_t`               | `uint16_t`                    | 无 | / |
| `u32`         | `uint32_t`               | `uint32_t`                    | 无 | / |
| `u64`         | `uint64_t`               | `uint64_t`                    | 无 | / |
| `f32`         | `float`                  | `float`                       | 无 | / |
| `f64`         | `double`                 | `double`                      | 无 | / |
| `bool`        | `bool`                   | `bool`                        | 无 | / |
| `String`      | `taihe::core::string`    | `taihe::core::string_view`    | 有 | 字符串类型，通过引用计数管理 |
| `Array<T>`    | `taihe::core::array<T>`  | `taihe::core::array_view<T>`  | 无 | 无引用计数的定长数组类型，拷贝时会同时复制其内部数据 |
| `Box<T>`      | `taihe::core::box<T>`    | `taihe::core::box_view<T>`    | 无 | 无引用计数的可空引用类型，拷贝时会同时复制其内部数据 |
| `Vector<T>`   | `taihe::core::vector<T>` | `taihe::core::vector_view<T>` | 有 | 通过引用计数管理的可变长数组 |
| `Map<K, V>`   | `taihe::core::map<K, V>` | `taihe::core::map_view<K, V>` | 有 | 通过引用计数管理的字典类型 |
| `Set<T>`      | `taihe::core::set<T>`    | `taihe::core::set_view<T>`    | 有 | 通过引用计数管理的集合类型 |
| `(a: A, b: B) => T` | `taihe::core::callback<T(A, B)>` | `taihe::core::callback_view<T(A, B)>` | 有 | 通过引用计数管理的函数闭包 |
| `struct S`    | `name::space::S`         | `const name::space::S &`      | 无 | 结构体，表示多个字段的组合 |
| `enum E`      | `name::space::E`         | `const name::space::E &`      | 无 | 联合体/枚举类型 |
| `interface I` | `name::space::I`         | `name::space::weak::I`        | 有 | 接口对象，通过引用计数管理 |
