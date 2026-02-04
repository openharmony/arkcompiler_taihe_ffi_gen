# 多继承（Multiple Inheritance）

> **学习目标**：掌握 Taihe 接口的多继承机制。

Taihe 的 interface 支持多继承。本教程以菱形继承为例进行介绍。

## 继承关系图

```
       IBase
      /     \
IColorable IShape
      \     /
       IRect
```

---

## 第一步：定义接口

**File: `idl/multiple_inherit.taihe`**

```rust
interface IBase {
    baseFunc(): void;
}

interface IColorable: IBase {
    getColor(): String;
}

interface IShape: IBase {
    getShape(): String;
}

interface IRect: IColorable, IShape {
    getMessage(): String;
}

function createIColorable(color: String): IColorable;
function createIShape(shape: String): IShape;
function createIRect(color: String, shape: String): IRect;
```

## 第二步：实现 C++ 代码

**File: `author/src/multiple_inherit.impl.cpp`**

```cpp
#include "multiple_inherit.impl.hpp"

using namespace taihe;
using namespace multiple_inherit;

class IColorableImpl {
public:
    IColorableImpl(string color = "None") : m_color(color) {}

    string getColor() { return m_color; }
    void baseFunc() { std::cout << "IColor" << std::endl; }

private:
    string m_color;
};

class IShapeImpl {
public:
    IShapeImpl(string shape = "None") : m_shape(shape) {}

    string getShape() { return m_shape; }
    void baseFunc() { std::cout << "IShape" << std::endl; }

private:
    string m_shape;
};

class IRectImpl {
public:
    IRectImpl(string color = "None", string shape = "None")
        : m_color(color), m_shape(shape) {}

    string getMessage() { return "It's Rect"; }
    string getColor() { return m_color; }
    string getShape() { return m_shape; }
    void baseFunc() { std::cout << "IRect" << std::endl; }

private:
    string m_color;
    string m_shape;
};

IColorable createIColorable(string_view color) {
    return make_holder<IColorableImpl, IColorable>(color);
}

IShape createIShape(string_view shape) {
    return make_holder<IShapeImpl, IShape>(shape);
}

IRect createIRect(string_view color, string_view shape) {
    return make_holder<IRectImpl, IRect>(color, shape);
}

TH_EXPORT_CPP_API_createIColorable(createIColorable);
TH_EXPORT_CPP_API_createIShape(createIShape);
TH_EXPORT_CPP_API_createIRect(createIRect);
```

> **说明**：C++ 实现类**无需继承关系**，只要实现对应的方法即可。如果希望通过继承复用代码也是允许的。

### 使用 C++ 继承的写法（可选）

```cpp
class IRectImpl : public IColorableImpl, public IShapeImpl {
public:
    IRectImpl(string color, string shape)
        : IColorableImpl(color), IShapeImpl(shape) {}

    string getMessage() { return "It's Rect"; }

    // 覆盖原有方法需要 override
    void baseFunc() override {
        std::cout << "IRect" << std::endl;
    }
};
```

## 第三步：编译运行

```sh
taihe-tryit test -u sts cookbook/multiple_inherit
```

## 使用示例

**File: `user/main.ets`**

```typescript
import * as multiple_inherit from "multiple_inherit";

loadLibrary("multiple_inherit");

function main() {
    let rect = multiple_inherit.createIRect("Red", "Square");
    
    console.log("Color: " + rect.getColor());    // Red
    console.log("Shape: " + rect.getShape());    // Square
    console.log("Message: " + rect.getMessage()); // It's Rect
}
```

**输出：**

```
Color: Red
Shape: Square
Message: It's Rect
```

---

## 相关文档

- [继承](../inherit/README.md) - 单继承基础
- [多态](../polymorphism/README.md) - 多态特性
