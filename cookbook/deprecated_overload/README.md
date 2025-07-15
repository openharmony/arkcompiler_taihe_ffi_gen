### 重载

重载（overload）指的是在同一个作用域中定义多个同名函数，但参数列表不同（参数类型或数量不同）。编译器会根据调用时传入的参数自动选择合适的函数。

taihe 为了保证与 C 语言兼容性，并不允许函数重载，但是 sts 侧允许重载，太和通过使用注解的方式支持 sts 侧重载

第一步 在 taihe 文件中声明
```taihe
@static_overload("add")
function sum_two(a: i32, b: i32): i32;
@static_overload("add")
function sum_arr(a: Array<i32>): i32;
```

sts 重载的注解如上述样例所示，使用 `@static_overload("{sts_name}")` 

使用该注解后，实现侧的函数名仍为 taihe 文件声明的函数名，但在 ets 侧会使用 `overload add {sum_two, sum_arr}` 实现 java-like 重载

第二步 实现声明的接口
```C++
int32_t sum_two(int32_t a, int32_t b) {
    return a + b;
}
int32_t sum_arr(array_view<int32_t> a) {
    if (a.size() == 0) return 0;
    int32_t result = 0;
    for (int i = 0; i < a.size(); ++i) {
        result += a[i];
    }
    return result;
}
```

第三步 生成并编译

```sh
# 注：taihe 文件里的函数与 C++ 规范一致，所以函数会在生成的 ets 侧自动转变为小写字母开头函数
# taihe 文件中的写法：
#   function FooBar(): void;
# 生成的 ets 侧代码
#   function fooBar(): void;
# 如果希望生成的 ets 侧函数与 taihe 文件一致，可以使用 --sts-keep-name
taihe-tryit test -u sts path/to/deprecated_overload --sts-keep-name
```

生成的 sts 代码如下：

```typescript
export native function _taihe_sum_two_native(a: int, b: int): int;
export native function _taihe_sum_arr_native(a: Array<int>): int;
export function sum_two(a: int, b: int): int {
    return _taihe_sum_two_native(a, b);
}
export function sum_arr(a: Array<int>): int {
    return _taihe_sum_arr_native(a);
}
export overload add {
    sum_two,
    sum_arr,
}
```

可以发现实现侧的 `sum_two` 函数和 `sum_arr` 函数绑定到 sts 的 add 函数的不同重载

用户侧使用

`main.ets`
```TypeScript
let a: int = 1
let b: int = 2
let numbers: int[] = [1, 2, 3, 4, 5];
console.log("add_two: " + overload.add(a, b))
console.log("add_arr: " + overload.add(numbers))
// Log output:
// add_two: 3
// add_arr: 15
```