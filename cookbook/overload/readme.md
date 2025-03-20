### 重载

重载(overload)指的是在同一个作用域中定义多个同名函数，但参数列表不同（参数类型或数量不同）。编译器会根据调用时传入的参数自动选择合适的函数。

taihe为了保证与C语言兼容性，并不允许函数重载，但是sts侧允许重载，太和通过使用注解的方式支持sts侧重载

第一步 在taihe文件中声明
```taihe
[sts_name = "add"]
function sum_two(a: i32, b: i32): i32;
[sts_name = "add"]
function sum_arr(Array<i32>): i32;
```

sts重载的注解如上述样例所示，使用`[sts_name = "{sts_name}"]` 

使用该注解后，实现侧的函数名仍为taihe文件声明的函数名，但在sts侧会绑定到`{sts_name}`名的函数

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

`compiler/`
```sh
./run-test /path/to/overload -ani
```

生成的sts代码如下：

```typescript
native function sum_two_inner(a: int, b: int): int;
export function add(a: int, b: int): int {
    return sum_two_inner(a, b);
}
native function sum_arr_inner(a: (int[])): int;
export function add(a: (int[])): int {
    return sum_arr_inner(a);
}
```

可以发现实现侧的`sum_two`函数和`sum_arr`函数绑定到sts的add函数的不同重载

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