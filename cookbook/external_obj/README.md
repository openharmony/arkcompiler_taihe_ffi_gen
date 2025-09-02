# External object

前面的章节中，我们讲述了 taihe 的类型，以及在实现侧如何使用这些类型

但是有一些情况下，我们希望在实现侧处理外部语言的对象，如：实现侧希望在 impl.cpp 里使用 ani 的对象

taihe 提供了 `ani runtime` 以及 `opaque` 类型用于在实现侧处理 ani 的对象

我们写一个简单的例子

## 第一步：在 Taihe IDL 文件中声明

**File: `idl/external_obj.taihe`**

```rust
@!sts_inject("import {Person} from 'other.subsystem';")

function is_string(s: Opaque): bool;
function get_objects(): Array<Opaque>;

function processPerson(person: @sts_type("Person") Opaque): void;
```

这里使用到的 Person 类型如下：

```typescript
export interface Person {
    name: string;
    age: number;
}
```

`Opaque` 类型可以理解为一个指针，可以用于指向一个外部语言的对象

| taihe 类型 |  C++ 侧投影   |  C++ 侧投影（作为参数时） |
|------------|--------------|-------------------------|
|  `Opaque`  | `uintptr_t`  |       `uintptr_t`       |

`@sts_inject` 注解用于将注解内的字符串写入生成的 sts 文件，`@!sts_inject` 添加注解到 当下的词法空间下，而 `@sts_inject`（注意，没有感叹号）将注解添加到下一个元素中。

`@sts_type` 注解用于指定 `Opaque` 在 sts 侧的类型，使用方法是在类型 `Opaque` 前面增加 `@sts_type("<type_name>")`，其中 `<type_name>` 为 sts 类型名

## 第二步：实现声明的接口

**File: `author/src/external_obj.impl.cpp`**

```cpp
// 判断输入的外部 ani 对象是否是 string 类型
bool is_string(uintptr_t a) {
    ani_env* env = get_env();
    ani_boolean res;
    ani_class cls;
    env->FindClass("std.core.String", &cls);
    env->Object_InstanceOf((ani_object)a, cls, &res);
    return res;
}

// 返回一个 array，索引 0 位置为一个 ani 的字符串，索引 1 位置为 undefined
array<uintptr_t> get_objects() {
    ani_env* env = get_env();
    ani_string ani_arr_0;
    env->String_NewUTF8("AAA", 3, &ani_arr_0);
    ani_ref ani_arr_1;
    env->GetUndefined(&ani_arr_1);
    return array<uintptr_t>({(uintptr_t)ani_arr_0, (uintptr_t)ani_arr_1});
}

// 使用 ANI 语法处理 person 类型对象
void processPerson(uintptr_t person) {
  ani_env* env = get_env();
  ani_object ani_obj = reinterpret_cast<ani_object>(person);
  ani_string name;
  ani_int age;
  env->Object_GetPropertyByName_Ref(ani_obj, "name",
                                    reinterpret_cast<ani_ref*>(&name));
  env->Object_GetPropertyByName_Int(ani_obj, "age", &age);
  ani_size len;
  env->String_GetUTF8Size(name, &len);
  char* name_utf8 = new char[len + 1];
  env->String_GetUTF8(name, name_utf8, len + 1, &len);
  std::cout << "name: " << name_utf8 << ", age: " << age << std::endl;
  delete[] name_utf8;
}
```

我们可以看到有 ani_env 类型、ani_string 类型等等，这些类型都是 ani 的类型，用户只需 `#include "taihe/runtime.hpp"` 即可使用

不同于 ani 侧的函数，我们可以发现函数参数并没有 `env`，所以，当用户希望在 impl.cpp 文件实现 ani 的部分逻辑时，需要使用 `ani_env* env = get_env();` 获取当前 `env`，其余按 ani 侧逻辑实现即可

## 第三步：生成并编译

```sh
# 注：Taihe IDL 文件里的函数与 C++ 规范一致，所以函数会在生成的 ets 侧自动转变为小写字母开头函数
# Taihe IDL 文件中的写法：
#   function FooBar(): void;
# 生成的 ets 侧代码
#   function fooBar(): void;
# 如果希望生成的 ets 侧函数与 Taihe IDL 文件一致，可以使用 -Csts:keep-name
taihe-tryit test -u sts path/to/external_obj -Csts:keep-name
```

用户侧使用

**File: `user/main.ets`**

```typescript
console.log(extobj.is_string("hello"));
console.log(extobj.is_string(123));

let person: Person = {name: "John", age: 30};
extobj.processPerson(person);
console.log(extobj.get_objects());
```

**Stdout**

```sh
true
false
name: John, age: 0
[AAA, undefined]
```
