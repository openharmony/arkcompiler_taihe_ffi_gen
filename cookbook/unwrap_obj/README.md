# 访问原生 C++ 对象（Unwrap Object）

> **学习目标**：掌握如何从 Taihe 接口中访问底层的原生 C++ 对象。

## 使用场景

当你有一个**已有的 C++ 类**（非 Taihe 设计），希望：
1. 通过 Taihe 接口暴露部分功能
2. 在实现内部访问 C++ 类的非暴露方法

这需要一种机制从接口对象中"取出"底层 C++ 实例。

---

## 第一步：定义接口

**File: `idl/wrap_interface.taihe`**

```rust
interface Foo {
    getInner(): i64;    // 关键：返回实现类指针
    func1(): String;
    func2(): String;
}

function makeFoo(): Foo;
function useFoo(obj: Foo): void;
```

> **说明**：`getInner(): i64` 是辅助方法，返回 C++ 实现类指针，仅供 C++ 内部使用。

## 第二步：实现 C++ 代码

**File: `author/src/wrap_interface.impl.cpp`**

```cpp
#include "wrap_interface.impl.hpp"

using namespace taihe;
using namespace wrap_interface;

// 已有的原生 C++ 类
class InnerFoo {
public:
    std::string func1() const { return "Hello from func1"; }
    std::string func2() const { return "Hello from func2"; }
    
    // 未暴露的方法
    void setName(std::string str) {
        name = str;
        std::cout << "Inner name: " << str << std::endl;
    }

private:
    std::string name;
};

// Taihe 接口实现类
class FooImpl {
public:
    FooImpl() : m_data(new InnerFoo()) {}
    ~FooImpl() { delete m_data; }

    // 返回 this 指针
    int64_t getInner() {
        return reinterpret_cast<int64_t>(this);
    }

    // 委托给 InnerFoo
    string func1() { return m_data->func1(); }
    string func2() { return m_data->func2(); }

private:
    friend void useFoo(weak::Foo);
    InnerFoo* m_data;
};

Foo makeFoo() {
    return make_holder<FooImpl, Foo>();
}

void useFoo(weak::Foo obj) {
    // 通过接口调用公开方法
    std::cout << obj->func1() << std::endl;
    std::cout << obj->func2() << std::endl;

    // 关键：通过 getInner() 获取实现类，访问未暴露功能
    FooImpl* impl = reinterpret_cast<FooImpl*>(obj->getInner());
    impl->m_data->setName("Tom");
}

TH_EXPORT_CPP_API_makeFoo(makeFoo);
TH_EXPORT_CPP_API_useFoo(useFoo);
```

### 关键步骤

1. **`getInner()`** 返回 `this` 指针（转为 `int64_t`）
2. **使用时** 通过 `reinterpret_cast` 转回实现类指针
3. **访问内部** 通过实现类指针访问原生 C++ 对象

## 第三步：编译运行

```sh
taihe-tryit test -u sts cookbook/wrap_interface
```

## 使用示例

**File: `user/main.ets`**

```typescript
import * as wrap_interface from "wrap_interface";

loadLibrary("wrap_interface");

function main() {
    let obj = wrap_interface.makeFoo();
    wrap_interface.useFoo(obj);
}
```

**输出：**

```
Hello from func1
Hello from func2
Inner name: Tom
```

---

## 安全注意事项

| 注意点 | 说明 |
|--------|------|
| 类型安全 | `reinterpret_cast` 必须转换到正确的类型 |
| 生命周期 | 确保接口对象生命周期覆盖指针使用范围 |
| 最小暴露 | 尽量通过接口方法暴露功能，避免直接访问实现类 |

---

## 相关文档

- [Interface 接口](../interface/README.md) - 接口定义
- [External Object](../external_obj/README.md) - 外部对象处理
