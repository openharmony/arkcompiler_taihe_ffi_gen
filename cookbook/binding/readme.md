### taihe如何实现方法的绑定

| 语言  |         ani         | taihe C++  | taihe C | c++ impl|
|-------|---------------------|-----------|---------|----------|
| 文件  | binding.ani.cpp | binding.proj.hpp | binding.abi.h | binding.impl.cpp |
| 函数  | `{"convert_color", nullptr, reinterpret_cast<void*>(binding_convert_color_ANIFunc1)}` | `binding::convert` | `binding_convert_color_f1` | `convert_color` |

用户实际调用链条为：

ets侧使用函数 `convert_color()` -> 

ani侧函数 `binding_convert_color_ANIFunc1()` -> 

taihe C++侧函数 `binding::convert()` -> 

taihe C侧函数 `binding_convert_color_f1()` -> 

实现侧函数 `convert_color()`

对应文件生成在`author_generated/`中

此外，为了方便实现侧开发，在`temp/`中有生成`.impl.cpp`的预实现，用户只需要将此文件里的函数实现改为自己的实现即可

`temp/binding.impl.cpp`
```C++
::binding::Color convert_color(::binding::Color const& a) {
    throw std::runtime_error("Function convert_color Not implemented");
    // author need to modify this implement, jest like:
    /*
    return ::binding::Color{ a.G, a.B, a.R };
    */
}
```

