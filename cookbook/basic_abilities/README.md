# taihe 基础能力

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
| `String`   | `taihe::string` | `taihe::string_view` |

注：目前 Taihe 在 C++ 侧支持 unsigned 类型，但是 ani 侧并不支持，如果用户进行开发，请避免使用 `u8`、`u16`、`u32`、`u64`. `array<u8>` 是一个特例，后续在 bytearray 章节会介绍
    
容器类型对应参照表

| Taihe 类型          |     C++ 侧投影             |     C++ 侧投影（作为参数时）     |
|---------------------|---------------------------|--------------------------------|
| `Array<T>`          | `taihe::array<T>`   | `taihe::array_view<T>`   |
| `Optional<T>`       | `taihe::optional<T>`| `taihe::optional_view<T>`|
| `Vector<T>`         | `taihe::vector<T>`  | `taihe::vector_view<T>`  |
| `Map<K, V>`         | `taihe::map<K, V>`  | `taihe::map_view<K, V>`  |
| `Set<T>`            | `taihe::set<T>`     | `taihe::set_view<T>`     |

我们可以发现，作为参数时，string 类型和容器类型的 Taihe 类型有 view 类型和非 view 类型，其中，view 类型的语义是不拥有所有权，只是对现有类型的引用，而非 view 类型则是拥有当前类型的所有权，用户可以根据使用场景来进行使用。

注：目前容器暂时只能用 array，其余容器后续会支持

依然是开发流程 3 步走

## 第一步 在 Taihe 文件中声明

`basic_abilities/idl/basic_abilities.taihe`
```taihe
function convert_arr(a: Array<i32>, str: String): Array<String>;
```

## 第二步 实现声明的函数

`basic_abilities/author/src/basic_abilities.impl.cpp`

```C++
array<string> convert_arr(array_view<int32_t> a, string_view str) {
    // 可通过 size() 获取 array 长度
    int32_t input_size = a.size();
    // 可以通过下标访问数组
    int32_t input_begin_val = a[0];
    int32_t input_end_val = a[input_size - 1];
    // 可以通过初始化列表创建数组
    array<string> res = { {std::to_string(input_size)}, 
        {std::to_string(input_begin_val)}, 
        {std::to_string(input_end_val)} , str};
    return res;
}
```

## 第三步 生成并编译

```sh
# 注：taihe 文件里的函数与 C++ 规范一致，所以函数会在生成的 ets 侧自动转变为小写字母开头函数
# taihe 文件中的写法：
#   function FooBar(): void;
# 生成的 ets 侧代码
#   function fooBar(): void;
# 如果希望生成的 ets 侧函数与 taihe 文件一致，可以使用 -Csts:keep-name
taihe-tryit test -u sts path/to/basic_abilities -Csts:keep-name
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

## Know more, Code better

在此例子中，我们使用了 string 和 array 用户可能对于实现侧对 Taihe string 和 array 有些困惑，在此介绍 Taihe runtime 的 string 和 array 类型在实现侧的使用

我们假设你已经拥有 C++ 的知识

### taihe string

1. string 使用引用计数进行自动的生命周期管理，用户只需要正常使用 string

2. 为方便用户使用，提供了许多相关的操作函数便于用户开发

    ```C++
    // example
    
    // 提供多种方式创建 string
    string s1("Hello");
    string s2("World", 5);
    string s3(std::string_view("C++"));
    string s4(std::string("Example"));

    // string 可以使用 << 输出
    std::cout << "s1: " << s1 << "\n";

    // 使用已有字符串为 string_view 进行 0 拷贝的初始化
    string_view sv1 = s1;

    // string_view 可以使用 << 输出
    std::cout << "sv1: " << sv1 << "\n";

    // 访问字符串首字符和尾字符
    std::cout << "s1 front: " << s1.front() << "\n";
    std::cout << "s1 back: " << s1.back() << "\n";

    // 连接字符串
    string s5 = s1 + s2;
    std::cout << "s1 + s2: " << s5 << "\n";

    // 截取子字符串
    string s6 = s5.substr(0, 5); // arg0: inputStr, arg1: begin position, arg2: len
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

3. 字符串分为 string 和 string_view，string 拥有字符串的所有权，而 string_view 不拥有字符串的所有权

    ```C++
    // example
    // string_view -> string 从不拥有所有权到拥有所有权会拷贝一次字符串，而反方向则不会进行拷贝
    string fun(string_view input) {
        return input; // 拷贝！
    }
    // 如果用户希望获得更好的性能，在不需要拷贝的场景则不使用 string 类型
    ```

### taihe array

1. 为方便用户使用，提供了许多相关的操作函数便于用户开发

    ```C++
    // example

    // 通过 std::vector 创建 array_view
    std::vector<double> vec = {3.14, 2.71, 1.62};
    array_view<double> view(vec);

    // 通过索引访问 array 内的元素
    std::cout << "Using operator[]: " << view[2] << "\n";
    // 通过 at() 访问 array 内的元素
    std::cout << "Using at(): " << view.at(1) << "\n";
    // 访问首元素
    std::cout << "Front: " << view.front() << "\n";
    // 访问尾元素
    std::cout << "Back: " << view.back() << "\n";
    // 获取数组大小
    std::cout << "Size: " << view.size() << "\n";

    // 使用初始化列表方式创建 array
    array<int> arr = {10, 20, 30, 40, 50}

    // 注意使用 begin(), end(), rbegin(), rend() 获取的是指针
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

2. 与 `string` 和 `string_view` 类似，`array` 拥有所有权，`array_view` 不拥有所有权
    ```C++
    // example

    // array_view -> array 从不拥有所有权到拥有所有权会拷贝一次字符串，而反方向则不会进行拷贝
    array fun(array_view input) {
        return input; // 拷贝！
    }
    // 如果用户希望获得更好的性能，在不需要拷贝的场景则不使用 array 类型
    ```
