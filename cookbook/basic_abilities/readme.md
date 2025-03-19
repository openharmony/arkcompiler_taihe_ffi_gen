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

注：目前taihe在c++侧支持unsigned类型，但是ani侧并不支持，如果用户进行开发，请避免使用`u8`、`u16`、`u32`、`u64`, `array<` `u8` `>`是一个特例，后续在bytearray章节会介绍
    
容器类型对应参照表

| taihe类型           |     C++ 侧投影             |     C++ 侧投影(作为参数时)      |
|---------------------|---------------------------|--------------------------------|
| `Array<T>`          | `taihe::core::array<T>`   | `taihe::core::array_view<T>`   |
| `Optional<T>`       | `taihe::core::optional<T>`| `taihe::core::optional_view<T>`|
| `Vector<T>`         | `taihe::core::vector<T>`  | `taihe::core::vector_view<T>`  |
| `Map<K, V>`         | `taihe::core::map<K, V>`  | `taihe::core::map_view<K, V>`  |
| `Set<T>`            | `taihe::core::set<T>`     | `taihe::core::set_view<T>`     |

我们可以发现，作为参数时，string类型和容器类型的taihe类型有view类型和非view类型，其中，view类型的语义是不拥有所有权，只是对现有类型的引用，而非view类型则是拥有当前类型的所有权，用户可以根据使用场景来进行使用。

注：目前容器暂时只能用array，其余容器后续会支持

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

### Know more, Code better

在此例子中，我们使用了 string 和 array 用户可能对于实现侧对taihe string 和 array 有些困惑，在此介绍taihe runtime 的 string 和 array 类型在实现侧的使用

我们假设你已经拥有C++的知识

#### taihe string

- 1 string使用引用计数进行自动的生命周期管理, 用户只需要正常使用string

- 2 为方便用户使用，提供了许多相关的操作函数便于用户开发

    ```C++
    // example
    
    // 提供多种方式创建string
    string s1("Hello");
    string s2("World", 5);
    string s3(std::string_view("C++"));
    string s4(std::string("Example"));

    // string可以使用 << 输出
    std::cout << "s1: " << s1 << "\n";

    // 使用已有字符串为string_view进行0拷贝的初始化
    string_view sv1 = s1;

    // string_view可以使用 << 输出
    std::cout << "sv1: " << sv1 << "\n";

    // 访问字符串首字符和尾字符
    std::cout << "s1 front: " << s1.front() << "\n";
    std::cout << "s1 back: " << s1.back() << "\n";

    // 连接字符串
    string s5 = concat(s1, s2);
    std::cout << "s1 + s2: " << s5 << "\n";

    // 截取子字符串
    string s6 = substr(s5, 0, 5); // arg0: inputStr, arg1: begin position, arg2: len
    std::cout << "Substring of s5 (first 5 chars): " << s6 << "\n";

    // 比较字符串
    std::cout << std::boolalpha;
    std::cout << "s1 == s2: " << (s1 == s2) << "\n";

    // 转换整数到 string
    string numStr = to_string(12345);
    std::cout << "to_string(12345): " << numStr << "\n";

    // 转换浮点数到 string
    string floatStr = to_string(3.1415);
    std::cout << "to_string(3.1415): " << floatStr << "\n";

    // 转换布尔值到 string
    string boolTrueStr = to_string(true);
    string boolFalseStr = to_string(false);
    std::cout << "to_string(true): " << boolTrueStr << "\n";
    std::cout << "to_string(false): " << boolFalseStr << "\n";
    ```


- 3 字符串分为string和string_view，string拥有字符串的所有权，而string_view不拥有字符串的所有权

    ```C++
    // example
    // string_view -> string 从不拥有所有权到拥有所有权会拷贝一次字符串，而反方向则不会进行拷贝
    string fun(string_view input) {
        return input; // 拷贝！
    }
    // 如果用户希望获得更好的性能，在不需要拷贝的场景则不使用string类型
    ```

#### taihe array

- 1 为方便用户使用，提供了许多相关的操作函数便于用户开发

    ```C++
    // example

    // 通过std::vector创建array_view
    std::vector<double> vec = {3.14, 2.71, 1.62};
    array_view<double> view(vec);

    // 通过索引访问array内的元素
    std::cout << "Using operator[]: " << view[2] << "\n";
    // 通过at()访问array内的元素
    std::cout << "Using at(): " << view.at(1) << "\n";
    // 访问首元素
    std::cout << "Front: " << view.front() << "\n";
    // 访问尾元素
    std::cout << "Back: " << view.back() << "\n";
    // 获取数组大小
    std::cout << "Size: " << view.size() << "\n";

    // 使用初始化列表方式创建array
    array<int> arr = {10, 20, 30, 40, 50}

    // 注意使用begin()、end()、rbegin()、rend()获取的是指针
    // 遍历
    std::cout << "Iterating using begin() and end(): ";
    for (auto it = arr.begin(); it != arr.end(); ++it) {
        std::cout << *it << " ";
    }
    std::cout << "\n";

    // 反向遍历
    std::cout << "Iterating using rbegin() and rend(): ";
    for (auto it = arr.rbegin(); it != arr.rend(); ++it) {
        std::cout << *it << " ";
    }
    ```

- 2 与 `string`和`string_view`类似，`array`拥有所有权，`array_view`不拥有所有权
    ```C++
    // example

    // array_view -> array 从不拥有所有权到拥有所有权会拷贝一次字符串，而反方向则不会进行拷贝
    array fun(array_view input) {
        return input; // 拷贝！
    }
    // 如果用户希望获得更好的性能，在不需要拷贝的场景则不使用array类型
    ```