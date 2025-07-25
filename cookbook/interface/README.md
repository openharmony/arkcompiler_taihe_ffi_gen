# Interface

在 [binding](../binding/README.md) 例子中已经有 struct 的例子了，这里介绍 taihe 的 interface 类型

依然是开发流程 3 步走

## 第一步 在 taihe 文件中声明

interface 需要写一个函数创建 interface 的实现，所以 `.taihe` 文件中需要有一个函数用于创建一个被实现的接口，如下方的 `makeIface` 函数

`interface/idl/interface.taihe`
```taihe
interface ICalculator {
    add(a: i32, b: i32): i32;
    sub(a: i32, b: i32): i32;
    getLastResult(): i32;
    reset(): void;
}

function makeCalculator(): ICalculator;
function restartCalculator(a: ICalculator): void;
```

## 第二步 实现声明的接口

需要写一个 class 实现接口，再使用 make_holder<class, interface>将实现和接口绑定

`interface/author/src/interface.impl.cpp`

```C++
class ICalculator {
public:
    ICalculator(int32_t init): lastResult(init){}
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

::interface::ICalculator makeCalculator(int32_t init) {
    return make_holder<ICalculator, ::interface::ICalculator>(init);
}
void restartCalculator(::interface::weak::ICalculator a) {
    a->reset();
}
```

- `make_holder<class, interface>` 是 taihe 提供的函数，用于将接口和实现绑定

- 实现侧的 interface 调用方法需要使用 `->` 调用，如 a->reset()，而不使用 `.` 调用

- 继承的子类使用父类方法时，需要先转换成父类才能使用父类方法

## 第三步 生成并编译

```sh
# 注：taihe 文件里的函数与 C++ 规范一致，所以函数会在生成的 ets 侧自动转变为小写字母开头函数
# taihe 文件中的写法：
#   function FooBar(): void;
# 生成的 ets 侧代码
#   function fooBar(): void;
# 如果希望生成的 ets 侧函数与 taihe 文件一致，可以使用 --sts-keep-name
taihe-tryit test -u sts path/to/interface --sts-keep-name
```

用户侧使用

`main.ets`
```TypeScript
let cal = makeCalculator();
let num1 = 1;
let num2 = 2;
let result1 = cal.add(num1, num2);
console.log("num1 + num2 = " + result1);
let result2 = cal.sub(num1, num2);
console.log("num1 - num2 = " + result2);
let result3 = cal.getLastResult();
console.log("Last calculation result: " + result3);
console.log("---restart_calculator---");
restartCalculator(cal);
let result4 = cal.getLastResult();
console.log("Last calculation result: " + result4);
// Log output:
// num1 + num2 = 3
// num1 - num2 = -1
// Last calculation result: -1
// ---restart_calculator---
// Last calculation result: 0
```