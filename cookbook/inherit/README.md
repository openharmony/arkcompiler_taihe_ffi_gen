# 继承

本章节会介绍继承，以银行卡付款为例子

## 第一步：编写接口原型

**File: `idl/inherit.taihe`**
```rust
interface Payable{
    pay(amountDue: f64): void;
}

@class
interface CreditCard : Payable {
    topUp(topUpAmount: f64): void;
    @get("banlance") getBalance(): f64;
    @get getIntlEnabled(): bool;
    @set setIntlEnabled(tag: bool): void;
}

function makeCreditCard(initAmount: f64): CreditCard;
```

我们已经知道 `@` 是 taihe 中注解的写法，这里我们解释 `@class` `@get` `@set` 三种注解

- `@class`

  对于上面的接口声明，如果不添加 `@class` 注解，那么在 ets 侧会默认投影成 `interface CreditCard`. 如果需要将其投影为 `class` 则需使用 `@class` 注解，使其在 ets 侧直接生成为 `class CreditCard`.

- `@get` 与 `@set`

  taihe 的 interface 中并不支持直接定义成员变量，但可以通过 `@get` 与 `@set` 注解来说明将某特定成员方法声明为某数据成员的 getter 或 setter，如样例中的 CreditCard 在 ets 侧会有一个只读变量 balance，以及一个可读写变量 intlEnabled.

  `@get` 和 `@set` 注解中可以有参数，表示该 getter 或 setter 所对应的数据成员名；也可以省略该参数，这种情况下，该方法名必须以 `get` 或 `set` 起始，对应的数据成员名会取方法名中 `get` 或 `set` 后的部分，然后将剩余部分的首字母小写（即按照小驼峰命名法）。

## 第二步：完成 C++ 实现

```cpp
class PayableImpl {
public:
    PayableImpl(double num) {}

    void pay(double amountDue) {}
private:
};

class CreditCardImpl {
public:
    CreditCardImpl(double num): amount(num), IntlEnabled(false) {}

    void topUp(double topUpAmount) {
        this->amount += topUpAmount;
    }

    double getBalance() {
        return this->amount;
    }

    bool getIntlEnabled() {
        return this->IntlEnabled;
    }

    void setIntlEnabled(bool tag) {
        this->IntlEnabled = tag;
    }

    // 允许重写父类方法
    void pay(double amountDue) {
        if (amountDue > this->amount) {
            std::cout << "Insufficient balance" << std::endl;
            return;
        }
        this->amount -= amountDue;
        std::cout << "Payment successful" << std::endl;
        return;
    }
private:
    double amount;
    bool IntlEnabled;
};

CreditCard makeCreditCard(double initAmount) {
    return make_holder<CreditCardImpl, CreditCard>(initAmount);
}
```

## 第三步：在 ets 侧使用

```typescript
// 初始化银行卡
let card = inherit.makeCreditCard(1000.0);
// 查看当前是否可以进行国际交易
console.log(card.intlEnabled);
// 设置为可进行国际交易
card.intlEnabled = true;
// 查看当前是否可以进行国际交易
console.log(card.intlEnabled);
// 查看余额
console.log(card.balance);
// 购买一件国际商品
console.log("Buy an international product")
card.pay(50.0); // 子 interface 可以直接调用父 inerface 的方法
// 查看余额
console.log(card.balance);
```

输出结果：
```sh
false
true
1000
Buy an international product
Payment successful
950
```

在 ets 侧，子 interface 可以直接调用父 interface 的方法，但是需要注意的是，在 C++ 侧，如果子类需要调用父类 interface 的方法，则需要手动转换一次

举例如下：
```cpp
CreditCard card = makeCreditCard(100.0);
// 如果想要调用 pay 方法，因为 pay 是通过继承得到的，在 C++ 侧需要转换为父类 interface
card->pay(50.0); // false!
weak::Payable(card)->pay(50.0); // success!（这里建议转换为父接口的 weak 类型以避免增加引用计数带来的开销）
```
