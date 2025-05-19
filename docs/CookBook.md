# Taihe Ani CookBook

## 1 hello world

### 1.1 一个简单的开始

我们假设你已经做好了如下准备:

- 1 对编程有一定了解; 
- 2 已经配置好了Taihe的环境配置.

Taihe可以生成各语言的绑定，使得API发布变得简单

开发流程3步走：

- 1 在`.taihe`文件写需要绑定的声明
- 2 在`impl.cpp`文件填写实现
- 3 生成代码并编译为lib


第一步 在taihe文件中声明

`hello_world/idl/hello_world.taihe`
```taihe
function add(a: i32, b: i32): String;
```

第二步 实现声明的函数

`hello_world/author/src/hello_world.impl.cpp`
```c++
string add(int32_t a, int32_t b) {
    std::string sum = std::to_string(a + b);
    return sum;
}
```

第三步 生成并编译

`compiler/`
```sh
./run-test /path/to/hello_world -ani
```

此时，用户只需要导入库就可以使用实现的函数了

`main.ets`
```TypeScript
let numA: Int = 1
let numB: Int = 2
// here
let sum = hello_world.add(numA, numB)
console.log("sum is : " + sum)
// log ouput: sum is : 3
```

参考示例：[Link](../cookbook/hello_world/)

### 1.2 taihe如何实现方法的绑定

| 语言  |         ani         | taihe C++  | taihe C | c++ impl|
|-------|---------------------|-----------|---------|----------|
| 文件  | hello_world.ani.cpp | hello_world.proj.hpp | hello_world.abi.h | hello_world.impl.cpp |
| 函数  | `{"add", nullptr, reinterpret_cast<void*>(hello_world_add_ANIFunc0)}` | `hello_world::add` | `hello_world_add_f0` | `add` |

用户实际调用链条为：

ets侧使用函数 `add()` -> 

ani侧函数 `hello_world_add_ANIFunc0()` -> 

taihe C++侧函数 `hello_world::add()` -> 

taihe C侧函数 `hello_world_add_f0()` -> 

实现侧函数 `add()`

对应文件生成在`generated/`中

此外，为了方便实现侧开发，在`temp/`中有生成`.impl.cpp`的预实现，用户只需要将此文件里的函数实现改为自己的实现即可

`temp/hello_world.impl.cpp`
```C++
string add(int32_t a, int32_t b) {
    throw std::runtime_error("Function add Not implemented");
    // author need to modify this implement, jest like:
    /* std::string sum = std::to_string(a + b);
     return sum; */
}
```

## 2 Taihe能力

### 2.1 基础类型与字符串

基础类型与字符串在第一章已有例子，下面只放类型对应参照表

| taihe 类型 | C++ 侧投影类型         | C++ 侧投影（作为参数时）     |
|------------|-----------------------|----------------------------|
| `i8`       | `int8_t`              | `int8_t`                   |
| `i16`      | `int16_t`             | `int16_t`                  |
| `i32`      | `int32_t`             | `int32_t`                  |
| `i64`      | `int64_t`             | `int64_t`                  |
| `u8`       | `uint8_t`             | `uint8_t`                  |
| `u16`      | `uint16_t`            | `uint16_t`                 |
| `u32`      | `uint32_t`            | `uint32_t`                 |
| `u64`      | `uint64_t`            | `uint64_t`                 |
| `f32`      | `float`               | `float`                    |
| `f64`      | `double`              | `double`                   |
| `bool`     | `bool`                | `bool`                     |
| `String`   | `taihe::string` | `taihe::string_view` |

### 2.2 容器

依然是开发流程3步走

第一步 在taihe文件中声明

`container_example/idl/container_example.taihe`
```taihe
function convert_arr(a: Array<i32>): Array<i32>;
```

第二步 实现声明的函数

`container_example/author/src/container_example.impl.cpp`

```C++
array<int32_t> convert_arr(array_view<int32_t> a) {
    // size() 可获取array长度
    int32_t input_size = a.size();
    // [] 可以通过下标访问数组
    int32_t input_begin_val = a[0];
    int32_t input_end_val = a[input_size - 1];
    // 可以通过初始化列表创建数组
    array<int32_t> res = { input_size, input_begin_val, input_end_val };
    return res;
}
```

第三步 生成并编译

`compiler/`
```sh
./run-test /path/to/container_example -ani
```

用户侧使用

`main.ets`
```TypeScript
let input_arr: int[] = [1, 2, 3, 4, 5]
let output_arr: int[] = container_example.convert_arr(input_arr)
for (let i = 0; i < output_arr.length; i++) {
    console.log("arr [" + i + "] val " + output_arr[i])
}
// Log output :
// arr [0] val 5
// arr [1] val 1
// arr [2] val 5
```

容器类型对应参照表

| taihe类型           |     C++ 侧投影             |     C++ 侧投影(作为参数时)      |
|---------------------|---------------------------|--------------------------------|
| `Array<T>`          | `taihe::array<T>`   | `taihe::array_view<T>`   |
| `Optional<T>`       | `taihe::optional<T>`| `taihe::optional_view<T>`|
| `Vector<T>`         | `taihe::vector<T>`  | `taihe::vector_view<T>`  |
| `Map<K, V>`         | `taihe::map<K, V>`  | `taihe::map_view<K, V>`  |
| `Set<T>`            | `taihe::set<T>`     | `taihe::set_view<T>`     |

参考示例：[Link](../cookbook/container_example/)

### 2.3 