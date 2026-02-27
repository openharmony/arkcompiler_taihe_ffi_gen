# Taihe 绑定机制

> **学习目标**：理解 Taihe 如何在 ArkTS 和 C++ 之间建立函数与类型的绑定关系。

本文档深入介绍 Taihe 的绑定原理，帮助你理解生成代码的结构和调用链。

## 函数的绑定

当你在 Taihe IDL 中定义一个函数时，Taihe 会生成多层代码来实现跨语言调用。

### 生成文件对照表

| 层级 | 文件 | 符号 |
|------|------|------|
| ANI 桥接层 | `binding.ani.cpp` | `binding_convert_color_ANIFunc1` |
| C++ 投影层 | `binding.proj.hpp` | `binding::convert` |
| C ABI 层 | `binding.abi.h` | `binding_convert_color_f1` |
| 用户实现 | `binding.impl.cpp` | `convert_color` |

### 调用链路

当 ArkTS 代码调用 `convert_color()` 函数时，实际执行路径为：

```
ArkTS: convert_color()
    ↓
ANI: binding_convert_color_ANIFunc1()
    ↓
C++: binding::convert()
    ↓
ABI: binding_convert_color_f1()
    ↓
实现: convert_color()
```

> **💡 提示**
>
> 生成的代码位于 `generated/` 目录，实现模板位于 `generated/temp/`。

### 实现示例

Taihe 会在 `temp/` 中生成实现模板，你只需填写业务逻辑：

```cpp
// temp/binding.impl.cpp

::binding::Color convert_color(::binding::Color const& a) {
    throw std::runtime_error("Function convert_color Not implemented");
    // 将此行替换为你的实现，例如：
    // return ::binding::Color{ a.G, a.B, a.R };
}
```

## 类型的绑定

以上例中的 `Color` 结构体为例，Taihe 同样会生成多层代码来实现类型的绑定：

### 生成文件对照表

| 层级 | 文件 | 符号 |
|------|------|------|
| C ABI | `binding.Color.abi.1.h` | `struct binding_Color_t` |
| C++ 投影 | `binding.Color.proj.1.hpp` | `binding::Color` |
| ANI 转换 | `binding.Color.ani.1.hpp` | `from_ani<Color>` / `into_ani<Color>` |

### 调用链路

```
ArkTS: new binding.Color(...)
    ↓
ANI: from_ani / into_ani
    ↓
C++: binding::Color
    ↓
ABI: struct binding_Color_t
```

---

## 相关文档

- [Hello World](../hello_world/README.md) - 快速入门示例
- [基础能力](../basic_abilities/README.md) - 类型映射详解
- [Interface 接口](../interface/README.md) - 接口绑定机制
