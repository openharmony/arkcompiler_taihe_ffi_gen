# Interface

在 [binding](../binding/README.md) 例子中已经有 struct 的例子了，这里介绍 taihe 的 interface 类型

依然是开发流程 3 步走

## 第一步：在 Taihe IDL 文件中声明

interface 需要写一个函数创建 interface 的实现，所以 `.taihe` 文件中需要有一个函数用于创建一个被实现的接口，如下方的 `makeIface` 函数

**File: `idl/interface.taihe`**

```rust
interface ICalculator {
    add(a: i32, b: i32): i32;
    sub(a: i32, b: i32): i32;
    getLastResult(): i32;
    reset(): void;
}

function makeCalculator(): ICalculator;
function restartCalculator(a: ICalculator): void;
```

## 第二步：实现声明的接口

需要写一个 class 实现接口，再使用 make_holder<class, interface> 将实现和接口绑定

**File: `author/src/interface.impl.cpp`**

```cpp
class MyCalculator {
public:
    // 构造函数可以有任意参数
    MyCalculator(int32_t init): lastResult(init){}

    int32_t add(int32_t a, int32_t b) {
        lastResult = a + b;
        return lastResult;
    }
    int32_t sub(int32_t a, int32_t b) {
        lastResult = a - b;
        return lastResult;
    }
    int32_t getLastResult() {
        return lastResult;
    }
    void reset() {
        lastResult = 0;
    }
private:
    int32_t lastResult = 0;
};

::interface::ICalculator makeCalculator() {
    // 使用 make_holder 将实现和接口绑定，调用参数为 MyCalculator 的构造函数参数
    return make_holder<MyCalculator, ::interface::ICalculator>(0);
}
void restartCalculator(::interface::weak::ICalculator a) {
    a->reset();
}
```

- `make_holder<class, interface>` 是 taihe 提供的函数，用于将接口和实现绑定

- 实现侧的 interface 调用方法需要使用 `->` 调用，如 a->reset()，而不使用 `.` 调用

- 继承的子类使用父类方法时，需要先转换成父类才能使用父类方法

## 第三步：生成并编译

```sh
# 注：Taihe IDL 文件里的函数与 C++ 规范一致，所以函数会在生成的 ets 侧自动转变为小写字母开头函数
# Taihe IDL 文件中的写法：
#   function FooBar(): void;
# 生成的 ets 侧代码
#   function fooBar(): void;
# 如果希望生成的 ets 侧函数与 Taihe IDL 文件一致，可以使用 -Csts:keep-name
taihe-tryit test -u sts path/to/interface -Csts:keep-name
```

用户侧使用

**File: `user/main.ets`**

```typescript
let cal = makeCalculator();
let num1 = 1;
let num2 = 2;
let result1 = cal.add(num1, num2);
console.log("num1 + num2 = " + result1);
let result2 = cal.sub(num1, num2);
console.log("num1 - num2 = " + result2);
let result3 = cal.getLastResult();
console.log("Last calculation result: " + result3);
console.log("--- restartCalculator ---");
restartCalculator(cal);
let result4 = cal.getLastResult();
console.log("Last calculation result: " + result4);
```

**Stdout**

```
num1 + num2 = 3
num1 - num2 = -1
Last calculation result: -1
--- restartCalculator ---
Last calculation result: 0
```
