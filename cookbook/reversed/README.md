# 外部 interface 实现在 C++ 侧调用

## 背景：用户已有实现

用户本身有声明文件，里面声明了一个 interface

```typescript
export interface IfaceA {
    foo(): string;
    bar(): int;
}
```

用户有对该接口实现的一个 class

```typescript
export class ClassA implements IfaceA {
    name: string = "";
    age: int;

    constructor(name: string, age: int) {
        this.name = name;
        this.age = age;
    }

    foo(): string {
        return this.name;
    }

    bar(): int {
        return this.age;
    }
}
```

现在我们希望在使用 taihe 后，在 C++ 代码调用 ets 侧的这些方法的实现

## 第一步：编写接口原型

被调用接口对应的 Taihe IDL 文件

**File: `idl/impl.taihe`**

```rust
interface IfaceA_taihe {
    Foo(): String;
    Bar(): i32;
}
```

注：此处的 interface 使用与原 interface 不同的名字

在 native 侧调用的对应 Taihe IDL 文件

**File: `idl/native_user.taihe`**

```rust
use impl;

function UseIfaceA(obj: impl.IfaceA_taihe): String;
```

## 第二步：完成 C++ 实现

impl.taihe 不需要手写 C++ 实现

**File: `author/src/native_user.impl.cpp`**

```cpp
::taihe::string UseIfaceA(::impl::weak::IfaceA_taihe obj) {
  std::cout << "native call Foo(): " << obj->Foo() << std::endl;
  std::cout << "native call Bar(): " << obj->Bar() << std::endl;
  return obj->Foo();
}
```

因为这个对象传递到 C++ 层时已经是一个 taihe C++ 对象了，所以可以使用 taihe C++ 的方式调用

```cpp
// 得到 weak 类型类对象
weak::Base weakBaseObj = baseObj;

// weak 类型转换为非 weak 类型
Base baseObj2 = Base(weakBaseObj);

// 子类转换为父类，静态转换
Base newDerivedOBj = Base(derivedOBj);

// 父类转换为子类，动态转换
Derived newDerivedOBj2 = Derived(newDerivedOBj);

// 调用函数 ->
baseObj->foo();
derivedOBj->foo(); // X 不允许子类直接调用父类函数，需要先转换为父类
derivedOBj->bar();
```

该示例就是使用了 `->` 调用相应的函数实现

## 第三步：ets 侧

修改原本的 class 实现

**File: `user/user_impl.ets`**

```typescript
import * as impl_taihe from "impl";

export class ClassA implements IfaceA, impl_taihe.IfaceA_taihe { // 新增 taihe 定义的 interface
    name: string = "";
    age: int;

    constructor(name: string, age: int) {
        this.name = name;
        this.age = age;
    }

    foo(): string {
        return this.name;
    }

    bar(): int {
        return this.age;
    }
}
```

原本是 `class ClassA implements IfaceA`，现在修改为 `class ClassA implements IfaceA, impl_taihe.IfaceA_taihe`

**File: `user/main.ets`**

```typescript
let obj: user_impl.IfaceA = new user_impl.ClassA("Tom", 18);
let objName: string = native_user.useIfaceA(obj);
console.log("ETS return: " + objName);
```
