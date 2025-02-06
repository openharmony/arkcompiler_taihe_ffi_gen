# 测试样例用户侧调用代码

本文档旨在帮助用户了解如何调用由 IDL 文件生成的代码。

---

## 1. 头文件

在使用模块前，需要导入对应的头文件。头文件遵循 `package.name.proj.hpp` 的命名格式：
```cpp
#include "integer.arithmetic.proj.hpp"
#include "integer.io.proj.hpp"
```

---

## 2. 函数调用

根据 IDL 文件中定义的函数名称和其所在命名空间调用函数。例如 `package::name::func_name()`。以下是一个示例：
```cpp
auto a = integer::io::input_i32();
auto b = integer::io::input_i32();
auto sum = integer::arithmetic::add_i32(a, b);
auto [quo, rem] = integer::arithmetic::divmod_i32(a, b);
integer::io::output_i32(sum);
```

---

## 3. 结构体

使用 IDL 文件中定义的结构体时，应调用对应命名空间下的结构体名称 `package::name::struct_name`。初始化结构体成员时使用花括号（`{}`）语法。

以下是一个示例，假设结构体定义在 `test/rgb` 的 `rgb.base.taihe` 文件中：
```cpp
rgb::base::RGB color_rgb = rgb::base::RGB{0x11, 0x45, 0x14};
```

---

## 4. 枚举类和联合体

### 4.1 构造枚举类/联合体对象

枚举类或联合体中的每个变体（variant）都有对应的构造方法。以下以 `test/rgb/idl` 目录下 `rgb.base.taihe` 文件中定义的变体 `ColorOrRGBOrName` 为例：

#### 4.1.1 使用工厂方法创建对象

可以通过类提供的静态工厂方法 `package::name::enum_name::make_variant_name(...)` 构造对应变体的对象。例如：
```cpp
rgb::base::ColorOrRGBOrName color_yellow = rgb::base::ColorOrRGBOrName::make_color(rgb::base::Color::make_yellow());
rgb::base::ColorOrRGBOrName color_114514 = rgb::base::ColorOrRGBOrName::make_rgb(RGB{0x11, 0x45, 0x14});
rgb::base::ColorOrRGBOrName color_miku = rgb::base::ColorOrRGBOrName::make_name("Miku");
rgb::base::ColorOrRGBOrName color_unknown = rgb::base::ColorOrRGBOrName::make_undefined();
```

#### 4.1.2 使用就地构造函数

也可以直接使用构造函数进行就地初始化。该方法的形式为：

```cpp
package::name::enum_name(taihe::core::static_tag<package::name::enum_name::tag_t::variant_name>, item_init_args, ...);
```

例如：

```cpp
rgb::base::ColorOrRGBOrName color_miku =
    rgb::base::ColorOrRGBOrName(taihe::core::static_tag<rgb::base::ColorOrRGBOrName::tag_t::name>, "Miku");
```

### 4.2 修改枚举类/联合体对象

已创建的对象可以通过 `emplace_variant_name(...)` 方法修改为其他变体。例如：

```cpp
color_miku.emplace_rgb(RGB{0x39, 0xC5, 0xBB});
```

### 4.3 检查对象当前的变体类型

可以使用 `holds_variant_name()` 方法判断当前对象是否为指定变体。返回值为 `bool` 类型。例如：

```cpp
bool is_name = color_miku.holds_name();
```

### 4.4 获取对象中的数据

#### 4.4.1 安全获取数据指针

使用 `get_variant_name_ptr()` 方法，如果当前对象是指定变体，则返回指向其数据的指针；否则返回空指针。例如：

```cpp
rgb::base::RGB* rgb_ptr = color_114514.get_rgb_ptr();
if (rgb_ptr != nullptr) {
    // 使用 rgb_ptr ...
}
```

#### 4.4.2 不安全获取数据指针

使用 `get_variant_name_ref()` 方法可以直接获取成员数据的引用，但不会检查变体类型是否正确。用户需要自行保证调用的正确性。例如：

```cpp
if (color_114514.holds_rgb()) {
    rgb::base::RGB& rgb_ref = color_114514.get_rgb_ref();
    // 使用 rgb_ptr ...
}
```

### 4.5 获取当前变体的标记（Tag）

使用 `get_tag()` 方法可以获取当前对象的变体标记，返回值类型为 `package::name::enum_name::tag_t`。例如：

```cpp
rgb::base::ColorOrRGBOrName::tag_t tag = color_miku.get_tag();
```

---

### 4.6 模板方法

上述方法均有等效的模板函数版本，形式如下：

```cpp
using ColorVariant = rgb::base::ColorOrRGBOrName;
using Tag = ColorVariant::tag_t;

ColorVariant color = ColorVariant::make<Tag::rgb>(RGB{0x11, 0x45, 0x14});
color.emplace<Tag::name>("Miku");
bool has_name = color.holds<Tag::name>();
auto* ptr = color.get_ptr<Tag::name>();
auto& ref = color.get_ref<Tag::name>();
```

---

## 5. 接口

用户可以通过实现 IDL 文件中定义的接口来自定义类。接口的实例化可以通过 `taihe::core::make_holder<impl_class, interface_1, interface_2, ...>(...)` 方法实现。以下是一个示例，仍以 `test/rgb/idl` 目录下 `rgb.show.taihe` 文件中定义的接口为例：

```cpp
class ColoredCircle {
public:
    // 任意的构造函数
    ColoredCircle(taihe:core::string_view id, float r, rgb::show::ColorOrRGBOrName const& color);

    // 在 IDL 中定义的接口方法
    taihe::core::string getId();
    float calculateArea();
    rgb::show::ColorOrRGBOrName getColor();
    void setColor(rgb::show::ColorOrRGBOrName const& color);
    void show();

    // 其他内部实现……
};

rgb::show::IShowable circle =
    taihe::core::make_holder<ColoredCircle, rgb::show::IShowable>("A", 10, color_114514);
```

### 5.1 接口的生命周期管理

接口对象的生命周期通过引用计数进行管理：

- **强引用**：`package::name::iface_name`，类似于 `std::shared_ptr`。
- **弱引用**：`package::name::weak::iface_name`，类似于 `std::weak_ptr`。

在参数传递时，为避免增加引用计数，可使用弱引用。例如：

```cpp
void copyColorImpl(rgb::base::weak::IColorable dst, rgb::base::weak::IColorable src) {
    dst.setColor(src.getColor());
}
```

### 5.2 接口的转换

接口支持以下两种转换：

1. **向上转换**：子接口到父接口间的转换是隐式、静态的。例如：
    ```cpp
    my::package::IDerived d0;
    my::package::weak::IBase b0 = d0; // OK
    ```

2. **其他转换**：除子接口向父接口的转换外，其他接口间的类型转换是动态的，需要显式写出，并需要在运行时检查转换后得到的对象是否有效。
    ```cpp
    my::package::IBase b1;
    my::package::weak::IDerived d1 = b1; // 错误，无法隐式从父接口转换为子接口
    auto d2 = my::package::weak::IDerived(b1); // OK
    if (d2) {
        // 转换成功
    } else {
        std::cout << "转换失败！" << std::endl;
    }
    ```

### 5.3 其他

在接口中的方法上添加 `[functor]` 属性可以使该方法成为一个函子，在 C++ 中即体现为对 `operator()` 方法的重载。

---

以上是使用 IDL 文件生成代码的主要方法和注意事项。如需更多帮助，请参考具体模块的文档或示例代码。
