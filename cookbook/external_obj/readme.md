### External object

前面的章节中，我们讲述了taihe的类型，以及在实现侧如何使用这些类型

但是有一些情况下，我们希望在实现侧处理外部语言的对象，如：实现侧希望在impl.cpp里使用ani的对象

taihe提供了 `ani runtime` 以及 `opaque` 类型用于在实现侧处理ani的对象

我们写一个简单的例子

第一步 在taihe文件中声明

```taihe
function is_string(s: Opaque): bool;
function get_objects(): Array<Opaque>;
```

`Opaque`类型可以理解为一个指针，可以用于指向一个外部语言的对象

| taihe类型 |   C++ 侧投影   | C++ 侧投影(作为参数时) |
|-----------|---------------|-----------------------|
| `Opaque`  | `uintptr_t`   |     `uintptr_t`       |

第二步 实现声明的接口

```C++
// 判断输入的外部ani对象是否是string类型
bool is_string(uintptr_t a) {
    ani_env* env = get_env();
    ani_boolean res;
    ani_class cls;
    env->FindClass("Lstd/core/String;", &cls);
    env->Object_InstanceOf((ani_object)a, cls, &res);
    return res;
}

// 返回一个array，索引0位置为一个ani的字符串，索引1位置为undefined
array<uintptr_t> get_objects() {
    ani_env* env = get_env();
    ani_string ani_arr_0;
    env->String_NewUTF8("AAA", 3, &ani_arr_0);
    ani_ref ani_arr_1;
    env->GetUndefined(&ani_arr_1);
    return array<uintptr_t>({(uintptr_t)ani_arr_0, (uintptr_t)ani_arr_1});
}
```

我们可以看到有ani_env类型、ani_string类型等等，这些类型都是ani的类型，用户只需`#include "core/runtime.hpp"`即可使用

不同于ani侧的函数，我们可以发现函数参数并没有`env`，所以，当用户希望在impl.cpp文件实现ani的部分逻辑时，需要使用 `ani_env* env = get_env();` 获取当前`env`，其余按ani侧逻辑实现即可

第三步 生成并编译

`compiler/`
```sh
./run-test /path/to/external_obj -ani
```

用户侧使用

`main.ets`
```TypeScript
console.log(extobj.is_string("hello"));
console.log(extobj.is_string(undefined));

console.log(extobj.get_objects());
// Log output:
// true
// false
// [AAA, undefined]
```