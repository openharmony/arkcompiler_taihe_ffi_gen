### Taihe 如何实现方法的绑定

| 语言 | ani | Taihe C++ | Taihe C | C++ impl |
|------|-----|-----------|---------|----------|
| 文件 | binding.ani.cpp | binding.proj.hpp | binding.abi.h | binding.impl.cpp |
| 函数 | `{"convert_color", nullptr, reinterpret_cast<void*>(binding_convert_color_ANIFunc1)}` | `binding::convert` | `binding_convert_color_f1` | `convert_color` |

用户实际调用链条为：

1. ets 侧使用函数 `convert_color()` 

2. ani 侧函数 `binding_convert_color_ANIFunc1()` 

3. taihe C++ 侧函数 `binding::convert()` 

4. taihe C 侧函数 `binding_convert_color_f1()` 

5. 实现侧函数 `convert_color()`

对应文件生成在 `generated/` 中

此外，为了方便实现侧开发，在 `temp/` 中有生成 `.impl.cpp` 的预实现，用户只需要将此文件里的函数实现改为自己的实现即可
```C++
// temp/binding.impl.cpp

::binding::Color convert_color(::binding::Color const& a) {
    throw std::runtime_error("Function convert_color Not implemented");
    // author need to modify this implement, e.g.
    // return ::binding::Color{ a.G, a.B, a.R };
}
```

### Taihe 如何实现 struct 的绑定

struct 在 Taihe 中是纯数据的，所以不需要用户在实现侧填写实现，使用者直接使用即可

| 语言 | ani | taihe C++ | taihe C |
|------|-----|-----------|---------|
| 文件 | binding.Color.ani.1.h | binding.Color.proj.1.hpp | binding.Color.abi.1.h |
| 函数 | `binding_Color_intoANI/fromANI` | `binding::Color` | `struct binding_Color_t` |

用户实际调用链条如下：

1. ets 侧使用 `new binding.Color`

2. ani 侧 `binding_Color_intoANI/fromANI()`

3. Taihe C++ 侧 `binding::Color`

4. Taihe C 侧函数 `struct binding_Color_t`
