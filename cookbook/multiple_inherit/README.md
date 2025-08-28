# 继承

Taihe 的 interface 支持多继承, 以一个简单的菱形继承为例介绍 Taihe interface 的多继承

## 第一步：编写接口原型

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

我们可以得到一个明显的菱形继承关系

```
       IBase
      /    \
IColorable IShape
      \    /
       IRect
```

## 第二步：完成 C++ 实现
**File: `author/src/multiple_inherit.impl.cpp`**
```cpp
class IBaseImpl {
    public:
    IBaseImpl() {}

    void baseFunc() {
        std::cout << "IBase" << std::endl;
    }
};

class IColorableImpl {
public:
    IColorableImpl(): m_color("None") {}

    IColorableImpl(::taihe::string color): m_color(color) {}

    ::taihe::string getColor() {
        return this->m_color;
    }

    void baseFunc() {
        std::cout << "IColor" << std::endl;
    }
private:
    ::taihe::string m_color;
};

class IShapeImpl {
public:
    IShapeImpl(): m_shape("None") {}

    IShapeImpl(::taihe::string shape): m_shape(shape) {}

    ::taihe::string getShape() {
        return this->m_shape;
    }

    void baseFunc() {
        std::cout << "IShape" << std::endl;
    }
private:
    ::taihe::string m_shape;
};

class IRectImpl {
    public:
    IRectImpl()
        : m_color("None"), m_shape("None") {}

    IRectImpl(::taihe::string color, ::taihe::string shape)
        : m_color(color), m_shape(shape) {}

    ::taihe::string getMessage() {
        return "It's Rect";
    }

    ::taihe::string getColor() {
        return this->m_color;
    }

    void baseFunc() {
        std::cout << "IRect" << std::endl;
    }

    ::taihe::string getShape() {
        return this->m_shape;
    }
private:
    ::taihe::string m_color;
    ::taihe::string m_shape;
};

::multiple_inherit::IColorable createIColorable(::taihe::string_view color) {
    return taihe::make_holder<IColorableImpl, ::multiple_inherit::IColorable>(color);
}

::multiple_inherit::IShape createIShape(::taihe::string_view shape) {
    return taihe::make_holder<IShapeImpl, ::multiple_inherit::IShape>(shape);
}

::multiple_inherit::IRect createIRect(::taihe::string_view color, ::taihe::string_view shape) {
    return taihe::make_holder<IRectImpl, ::multiple_inherit::IRect>(color, shape);
}
```

Taihe 的 C++ 实现侧与 Taihe 的 interface 是接口与实现的关系，Taihe 会将实现的对应名字的函数绑定到 Taihe 的 interface 对象上

额外信息: C++ 实现侧的 impl 类直接是**允许没有继承关系**的，只要实现对应的方法就能够成功绑定, 用户在 C++ 实现时如果希望通过继承来完成现有方法的复用在 Taihe 也是允许的，代码如下：

```cpp
class IColorableImpl {
public:
    IColorableImpl(): m_color("None") {}

    IColorableImpl(::taihe::string color): m_color(color) {}

    virtual ::taihe::string getColor() {
        return this->m_color;
    }

    virtual void baseFunc() {
        std::cout << "IColor" << std::endl;
    }
private:
    ::taihe::string m_color;
};

class IShapeImpl {
public:
    IShapeImpl(): m_shape("None") {}

    IShapeImpl(::taihe::string shape): m_shape(shape) {}

    virtual ::taihe::string getShape() {
        return this->m_shape;
    }

    virtual void baseFunc() {
        std::cout << "IShape" << std::endl;
    }
private:
    ::taihe::string m_shape;
};

class IRectImpl: public IColorableImpl, public IShapeImpl {
    public:
    IRectImpl()
        : IColorableImpl("None"), IShapeImpl("None") {}

    IRectImpl(::taihe::string color, ::taihe::string shape)
        : IColorableImpl(color), IShapeImpl(shape) {}

    virtual ::taihe::string getMessage() {
        return "It's Rect";
    }

    // 注：覆盖原有函数实现需要记得写 override
    virtual void baseFunc() override {
        std::cout << "IRect" << std::endl;
    }
};
```


## 第三步：在 ets 侧使用

```typescript
let Obj = multiple_inherit.createIRect("Red", "Square");
console.log("Obj's Color is: " + Obj.getColor());
console.log("Obj's Shape is: " + Obj.getShape());
console.log("Obj's Message is: " + Obj.getMessage());
```

输出结果：
```sh
Obj's Color is: Red
Obj's Shape is: Square
Obj's Message is: It's Rect
```
