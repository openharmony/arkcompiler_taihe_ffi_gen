# 太和 C++ 用户文档

本文档旨在帮助用户了解如何调用由 IDL 文件生成的代码。

## 1. 生成的文件结构

在使用模块前，需要导入对应的头文件。头文件名与 IDL 文件的包名相关，例如，假设 IDL 文件名为 `rgb.base.taihe`，则 `generated/include` 目录下可能生成以下头文件：

```
generated/include/rgb.base.proj.hpp
generated/include/rgb.base.user.hpp
generated/include/rgb.base.impl.hpp
```

这些文件对于使用者的意义如下：
- 对于接口的作者（发布方），需要关注的是 `proj.hpp` 和 `impl.hpp`，其中 `proj.hpp` 包含了当前包下定义的所有类型（包括枚举类、结构体、联合体、接口等，使用方式见后文）的 C++ 声明和定义，而 `impl.hpp` 则提供了用于导出全局函数的宏定义。
- 对于接口的用户（消费方），只需要关注 `user.hpp`，该文件包含了 `proj.hpp` 中的所有内容，此外还允许用户直接调用全局函数（见第 6 节）。

> **⚠️ 特别注意**
>
> 除这些文件之外，`generated/include` 目录下还可能包含其他头文件，这些文件通常对应于 IDL 文件中定义的特定类型，例如 `rgb.base.IShowable.{0,1,2}.hpp` 等，这些文件是太和的内部实现文件，用户通常***不应该***直接使用它们，并且我们也***不保证***这些文件的稳定性，它们可能会在未来的版本中发生变化。

## 2. 枚举类

假设在 IDL 文件中定义了一个枚举类 `Color`，其定义如下：
```ts
enum Color: String {
    BLACK = "black",
    RED = "red",
    GREEN = "green",
    YELLOW = "yellow",
    BLUE = "blue",
    MAGENTA = "magenta",
    CYAN = "cyan",
    WHITE = "white",
}
```

### 2.1 构造

#### 2.1.1 通过 Key 初始化对象

可以通过如下方式，直接根据枚举值来创建枚举类对象：
```cpp
rgb::base::Color yellow = rgb::base::Color::key_t::YELLOW;
```

#### 2.1.2 通过 Value 初始化对象

也可以通过值初始化枚举类对象：
```cpp
auto yellow = rgb::base::Color::from_value("yellow");
```

### 2.2 枚举类的成员函数

#### 2.2.1 获取枚举值

可以使用 `get_value()` 方法获取枚举值：
```cpp
uint8_t value = yellow.get_value();  // "yellow"
```

#### 2.2.2 获取对象的 Key

可以使用 `get_key()` 方法获取枚举类对象的 Key：
```cpp
rgb::base::Color::key_t key = yellow.get_key();

switch (key) {
    case rgb::base::Color::key_t::BLACK: break;
    case rgb::base::Color::key_t::RED: break;
    case rgb::base::Color::key_t::GREEN: break;
    case rgb::base::Color::key_t::YELLOW: break;
    case rgb::base::Color::key_t::BLUE: break;
    case rgb::base::Color::key_t::MAGENTA: break;
    case rgb::base::Color::key_t::CYAN: break;
    case rgb::base::Color::key_t::WHITE: break;
    default: break;
}
```

> **💡 提示：Key 与 Value 的区别**
>
> - **Key**
>   枚举项的名称，例如 `Color::key_t::YELLOW`。它是一个强类型，可以安全地用于 `switch` 语句。
> - **Value**
>   枚举项关联的值，例如 `"yellow"`。
>
> 特别注意，对于整数类型的枚举，将 Key 强制转换为整数得到的是**索引（index）**，而非其**值（value）**。
>
> #### IDL 示例：
> ```ts
> enum IntEnum: i32 {
>     FOO = 12, // index 0
>     BAR = 34, // index 1
> }
> ```
>
> #### C++ 中：
> ```cpp
> auto key = IntEnum::key_t::FOO;
> int index = static_cast<int>(key); // 结果是 0, 而不是 12
> int value = IntEnum(key).get_value(); // 结果是 12
> ```


#### 2.2.3 判断枚举值是否有效
可以使用 `is_valid()` 方法判断一个枚举对象是否有效的：

```cpp
auto yellow = rgb::base::Color::from_value("yellow");
auto purple = rgb::base::Color::from_value("purple");
rgb::base::Color color_7 = reinterpret_cast<rgb::base::Color::key_t>(7);
rgb::base::Color color_8 = reinterpret_cast<rgb::base::Color::key_t>(8);

bool yellow_is_valid = yellow.is_valid();  // true
char const* yellow_value = yellow.get_value();  // "yellow"

bool purple_is_valid = purple.is_valid();  // false
char const* purple_value = purple.get_value();  // will cause undefined behavior

bool color_7_is_valid = color_7.is_valid();  // true
char const* color_7_value = color_7.get_value();  // "white"

bool color_8_is_valid = color_8.is_valid();  // false
char const* color_8_value = color_8.get_value();  // will cause undefined behavior
```

## 3. 结构体

使用 IDL 文件中定义的结构体时，应使用对应命名空间下的结构体名称 `package::name::StructName`。你可以像使用 C++ 原生结构体那样使用它们。初始化结构体成员时使用花括号（`{}`）语法。

以下是一个示例，假设结构体在 IDL 中的定义如下：
```ts
struct RGB {
    red: u8;
    green: u8;
    blue: u8;
}
```

可以在 C++ 中这样创建和初始化结构体对象：
```cpp
rgb::base::RGB color_rgb = rgb::base::RGB{0x39, 0xC5, 0xBB};

// 或者使用命名初始化
rgb::base::RGB color_rgb = rgb::base::RGB{
    .red = 0x39,
    .green = 0xC5,
    .blue = 0xBB,
};
```

## 4. 联合体

### 4.1 构造联合体对象

联合体中的每个变体（variant）都有对应的构造方法。例如，对于在 IDL 中以如下方式定义的联合体：
```ts
union RGBOrColorOrName {
    rgb: RGB;
    color: Color;
    name: String;
    unknown;
}
```

#### 4.1.1 使用工厂方法创建对象

可以通过类提供的静态工厂方法 `package::name::EnumName::make_variantName(...)` 构造对应变体的对象。例如：
```cpp
auto color_114514 = rgb::base::RGBOrColorOrName::make_rgb(RGB{0x11, 0x45, 0x14});
auto color_yellow = rgb::base::RGBOrColorOrName::make_color(rgb::base::Color::key_t::YELLOW);
auto color_miku = rgb::base::RGBOrColorOrName::make_name("Miku");
auto color_unknown = rgb::base::RGBOrColorOrName::make_unknown();
```

#### 4.1.2 使用就地构造函数

也可以直接使用构造函数进行就地初始化。该方法的形式为：
```cpp
package::name::EnumName(taihe::static_tag<package::name::EnumName::tag_t::variantName>, item_init_args, ...);
```

例如：
```cpp
auto color_miku =
    rgb::base::RGBOrColorOrName(taihe::static_tag<rgb::base::RGBOrColorOrName::tag_t::name>, "Miku");
```

### 4.2 修改枚举类/联合体对象

已创建的对象可以通过 `emplace_variantName(...)` 方法修改为其他变体。例如：
```cpp
color_miku.emplace_rgb(RGB{0x39, 0xC5, 0xBB});
```

### 4.3 检查对象当前的变体类型

可以使用 `holds_variantName()` 方法判断当前对象是否为指定变体。返回值为 `bool` 类型。例如：
```cpp
bool is_name = color_miku.holds_name();
```

### 4.4 获取对象中的数据

#### 4.4.1 安全获取数据指针

使用 `get_variantName_ptr()` 方法，如果当前对象是指定变体，则返回指向其数据的指针；否则返回空指针。例如：
```cpp
rgb::base::RGB* rgb_ptr = color_114515.get_rgb_ptr();
if (rgb_ptr != nullptr) {
    // 使用 rgb_ptr ...
}
```

#### 4.4.2 不安全获取数据指针

使用 `get_variantName_ref()` 方法可以直接获取成员数据的引用，但不会检查变体类型是否正确。用户需要自行保证调用的正确性。例如：
```cpp
if (color_114515.holds_rgb()) {
    rgb::base::RGB& rgb_ref = color_114515.get_rgb_ref();
    // 使用 rgb_ptr ...
}
```

### 4.5 获取当前变体的标记（Tag）

使用 `get_tag()` 方法可以获取当前对象的变体标记，返回值类型为 `package::name::EnumName::tag_t`。例如：
```cpp
rgb::base::RGBOrColorOrName::tag_t tag = color_miku.get_tag();
```

### 4.6 模板方法

上述方法均有等效的模板函数版本，形式如下：
```cpp
using ColorVariant = rgb::base::RGBOrColorOrName;
using Tag = ColorVariant::tag_t;

// 等效于 ColorVariant::make_rgb(RGB{0x11, 0x45, 0x14})
ColorVariant color = ColorVariant::make<Tag::rgb>(RGB{0x11, 0x45, 0x14});

// 等效于 color.emplace_name("Miku")
color.emplace<Tag::name>("Miku");

// 等效于 color.holds_name()
bool is_name = color.holds<Tag::name>();

// 等效于 color.get_name_ptr()
auto* ptr = color.get_ptr<Tag::name>();

// 等效于 color.get_name_ref()
auto& ref = color.get_ref<Tag::name>();
```

## 5. 接口

用户可以通过实现 IDL 文件中定义的接口来自定义类。接口的实例化可以通过 `taihe::make_holder<ImplClass, InterfaceA, InterfaceB, ...>(...)` 方法实现。其中 `InterfaceA`, `InterfaceB` 等为 IDL 中定义的接口，`ImplClass` 为用户自定义的类，该类需要实现所有接口中定义的方法。

以下是一个示例，假定 IDL 文件中定义了一个接口 `IShowable`，其定义如下：
```ts
interface IHasColor {
    getColor(): RGBOrColorOrName;
    setColor(color: RGBOrColorOrName);
}

interface IShape {
    getId(): String;
    calculateArea(): f32;
}

interface IShowable: IHasColor, IShape {
    show();
}
```

在 C++ 中实现该接口的类 `ColoredCircle` 如下：
```cpp
class ColoredCircle {
public:
    // 任意的构造函数
    ColoredCircle(taihe:core::string_view id, float r, rgb::show::RGBOrColorOrName const& color);

    // 在 IDL 中定义的接口方法
    taihe::string getId();
    float calculateArea();
    rgb::show::RGBOrColorOrName getColor();
    void setColor(rgb::show::RGBOrColorOrName const& color);
    void show();

    // 其他内部实现……
};

// 创建接口对象
rgb::show::IShowable circle =
    taihe::make_holder<ColoredCircle, rgb::show::IShowable>("myCircle", 10, color_114514);

// 调用接口方法
circle->show();
```

### 5.1 接口的生命周期管理

接口对象的生命周期通过引用计数进行管理，对于每个在 IDL 文件中定义的接口，太和会生成两种对应的类型：

- **强引用**：`package::name::interfaceName`，类似于 `std::shared_ptr`。
- **弱引用**：`package::name::weak::interfaceName`，类似于 `std::weak_ptr`。

在参数传递时，为避免增加引用计数，可使用弱引用。例如：
```cpp
void copyColorImpl(rgb::base::weak::IColorable dst, rgb::base::weak::IColorable src) {
    dst->setColor(src->getColor());
}
```

### 5.2 接口的转换

接口支持以下两种转换：

- **静态转换**：子接口到父接口间的转换是隐式、静态的。例如：
  ```cpp
  my::package::IDerived d0;

  my::package::IBase b0 = d0; // OK
  my::package::weak::IBase b0 = d0; // OK
  ```

- **动态转换**：除子接口向父接口的转换外，其他接口间的类型转换是动态的，需要显式写出，并需要在运行时检查转换后得到的对象是否有效。
  ```cpp
  my::package::IBase b1;
  my::package::weak::IDerived d1 = b1; // Error: 无法隐式从父接口转换为子接口
  auto d2 = my::package::weak::IDerived(b1); // OK
  if (!d2.is_error()) {  // 通过 is_error() 检查转换是否成功
      // 转换成功，可以使用 d2
      std::cout << "Conversion succeeded!" << std::endl;
  } else {
      // 转换失败，b1 不是 IDerived 的实例
      std::cerr << "Conversion failed!" << std::endl;
  }
  ```

### 5.3 接口方法的调用

通过 `->` 运算符调用接口自己的方法。例如：
```cpp
rgb::show::IShowable circle =
    taihe::make_holder<ColoredCircle, rgb::show::IShowable>("myCircle", 10, color_114514);
circle->show();
```

> **💡 调用父接口的方法**
>
> 您不能直接在子接口上调用父接口的方法。必须先将接口转换为父接口类型，然后再调用。
> ```cpp
> // 错误
> circle->calculateArea();
>
> // 正确
> rgb::show::weak::IShape shape = circle; // 静态转换为父接口
> float area = shape->calculateArea();
> ```

### 5.4 同时实现多个接口

如果在 `file.taihe` 中定义了 `IReadable` 和 `IWritable` 两个接口：
```ts
interface IReadable {
    read(): String;
}
interface IWritable {
    write(data: String);
}
```

在 C++ 中可以实现一个类同时实现这两个接口的方法：
```cpp
class FileHandler {
public:
    FileHandler(taihe::string_view filename);
    taihe::string read();
    void write(taihe::string_view data);
};
```

然后使用 `taihe::make_holder` 创建一个同时实现这两个接口的对象：
```cpp
auto fileHandler = taihe::make_holder<FileHandler, rgb::show::IReadable, rgb::show::IWritable>("file.txt");

rgb::show::IReadable readable = fileHandler;  // OK
rgb::show::IWritable writable = fileHandler;  // OK

// 调用接口方法
writable->write("Hello, Taihe!");
taihe::string content = readable->read();

// 它们本质上指向同一个对象，可以动态转换
auto readableAsWritable = rgb::show::weak::IWritable(readable);
bool isWritable = not readableAsWritable.is_error();  // true
auto writableAsReadable = rgb::show::weak::IReadable(writable);
bool isReadable = not writableAsReadable.is_error();  // true
```

## 6. 使用全局函数

### 6.1 导出函数（接口发布方）

如果你是接口的作者（发布方），需要将函数导出以供用户调用。可以使用 `package.name.user.hpp` 中定义的宏 `TH_EXPORT_CPP_API_funcName(func)` 来导出函数，其中 `func` 是你实现的函数名。

例如，假设你在 IDL 文件中定义了一个函数 `divmod_i32`：
```ts
struct DivModResult {
    quo: i32;
    rem: i32;
}
function divmod_i32(a: i32, b: i32): DivModResult;
```

你可以在 C++ 实现文件中这样导出该函数：
```cpp
#include "integer.arithmetic.proj.hpp"
#include "integer.arithmetic.impl.hpp"

integer::arithmetic::DivModResult ohos_int_divmod(int32_t a, int32_t b) {
    return { a / b, a % b };
}

TH_EXPORT_CPP_API_divmod_i32(ohos_int_divmod)
```

### 6.2 调用函数（接口消费方）

接口的使用方可以导入头文件 `package.name.user.hpp`，并根据 IDL 文件中定义的函数名称和其所在的命名空间来调用函数。如 `package::name::funcName()`。例如，假设你要调用第 5 节中定义的 `divmod_i32` 函数，可以这样写：
```cpp
#include <iostream>

#include "integer.arithmetic.user.hpp"

int main() {
    int32_t a = 10;
    int32_t b = 3;

    integer::arithmetic::DivModResult result = integer::arithmetic::divmod_i32(a, b);

    std::cout << "Quotient = " << result.quo << std::endl;
    std::cout << "Remainder = " << result.rem << std::endl;

    return 0;
}
```

---

以上是使用 IDL 文件生成代码的主要方法和注意事项。如需更多帮助，请参考具体模块的文档或示例代码。
