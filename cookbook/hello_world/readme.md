### 一个简单的开始

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

### taihe如何实现方法的绑定

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

对应文件生成在`author_generated/`中

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
