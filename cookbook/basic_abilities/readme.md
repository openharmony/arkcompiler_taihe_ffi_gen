### taihe基础能力

类型对应参照表

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
| `String`   | `taihe::core::string` | `taihe::core::string_view` |
    
容器类型对应参照表

| taihe类型           |     C++ 侧投影             |     C++ 侧投影(作为参数时)      |
|---------------------|---------------------------|--------------------------------|
| `Array<T>`          | `taihe::core::array<T>`   | `taihe::core::array_view<T>`   |
| `Optional<T>`       | `taihe::core::optional<T>`| `taihe::core::optional_view<T>`|
| `Vector<T>`         | `taihe::core::vector<T>`  | `taihe::core::vector_view<T>`  |
| `Map<K, V>`         | `taihe::core::map<K, V>`  | `taihe::core::map_view<K, V>`  |
| `Set<T>`            | `taihe::core::set<T>`     | `taihe::core::set_view<T>`     |

依然是开发流程3步走

第一步 在taihe文件中声明

`basic_abilities/idl/basic_abilities.taihe`
```taihe
function convert_arr(a: Array<i32>, str: String): Array<String>;
```

<!-- function get_vec(): Vector<Optional<f32>>;
function get_map(): Map<i32, String>;
function get_set(): Set<i32>;
``` -->

第二步 实现声明的函数

`basic_abilities/author/src/basic_abilities.impl.cpp`

```C++
array<string> convert_arr(array_view<int32_t> a, string_view str) {
    // size() 可获取array长度
    int32_t input_size = a.size();
    // [] 可以通过下标访问数组
    int32_t input_begin_val = a[0];
    int32_t input_end_val = a[input_size - 1];
    // 可以通过初始化列表创建数组
    array<string> res = { {std::to_string(input_size)}, 
        {std::to_string(input_begin_val)}, 
        {std::to_string(input_end_val)} , str};
    return res;
}
```

第三步 生成并编译

`compiler/`
```sh
./run-test /path/to/basic_abilities -ani
```

用户侧使用

`main.ets`
```TypeScript
let input_arr: int[] = [1, 2, 3, 4, 5]
let input_str: String = "hello"
let output_arr: String[] = basic_abilities.convert_arr(input_arr, input_str)
for (let i = 0; i < output_arr.length; i++) {
    console.log("arr [" + i + "] val " + output_arr[i])
}
// Log output :
// arr [0] val 5
// arr [1] val 1
// arr [2] val 5
// arr [3] val hello
```