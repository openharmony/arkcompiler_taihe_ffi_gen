# 外部对象导出
在实践的过程中，会有使用已经实现的 class 的情况

## 第一步：编写接口原型

**File: `idl/wrap_interface.taihe`**
```taihe
interface Foo{
    getInner(): i64;
    func1(): String;
    func2(): String;
}

function makeFoo(): Foo;
function useFoo(obj: Foo): void;
```
该场景中，实际上在 `useFoo` 函数中需要使用到已经实现的类

我们在这种情况下，需要给 `interface Foo` 增加一个 `GetInner()` 的方法，返回类型为 `i64`, 用于返回实现类

## 第二步：完成 C++ 实现

假设已经实现好的类 `InnerFoo` 如下所示：

**File: `idl/wrap_interface.impl.cpp`**
```C++
// 已经实现的类
class InnerFoo {
public:
    std::string func1() const {
        return "Hello from func1";
    }

    std::string func2() const {
        return "Hello from func2";
    }
    void setName(std::string str) {
        this->name = str;
        std::cout << "Inner Class's name is " << str << std::endl;
    }
private:
    std::string name;
};
```

Taihe实现侧为：

**File: `idl/wrap_interface.impl.cpp`**
```C++
// Taihe interface实现类
class FooImpl {
public:
    FooImpl() {
        m_data = new InnerClass();
    }

    // 使用类型转换将类指针转换为 int64_t 类型
    int64_t getInner() {
        return reinterpret_cast<int64_t>(this);
    }

    string func1() {
        return this->m_data->func1();
    }

    string func2() {
        return this->m_data->func2();
    }
private:
    friend void useFoo(weak::Foo);
    InnerFoo* m_data;
};

Foo makeFoo() {
    return make_holder<FooImpl, Foo>();
}

void useFoo(weak::Foo obj) {
    std::cout << obj->func1() << std::endl;
    std::cout << obj->func2() << std::endl;
    // 使用getInner()然后类型转换为taihe实现类指针
    reinterpret_cast<FooImpl*>(obj->getInner())->m_data->setName("Tom");
    return ;
}
```

使用 `getInner()` 方法输出实现类的指针

我们也可以看到 `useFoo()` 函数里面能够成功获取 `InnerFoo` 以及调用其方法 `setName`

## 第三步：在 ets 侧使用

```typescript
// 创建对象
let obj = wrap_interface.makeFoo();
// 调用函数
wrap_interface.useFoo(obj);
```

Output:
```sh
Hello from func1
Hello from func2
Inner Class's name is Tom
```