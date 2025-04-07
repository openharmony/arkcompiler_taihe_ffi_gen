# 继承

本章节会介绍继承，以银行卡付款为例子

## 第一步：编写接口原型

**File: `idl/inherit.taihe`**
```taihe
interface Payable{
    pay(amountDue: f64): void;
}

@class
interface CreditCard : Payable {
    topUp(topUpAmount: f64): void;
    @get getBalance(): f64;
    @get getIntlEnabled(): bool;
    @set setIntlEnabled(tag: bool): void;
}

function makeCreditCard(initAmount: f64): CreditCard;
```

我们已经知道@是 taihe 的注释，这里我们解释 `@class` `@get` `@set` 三种注释

`@class` taihe 是接口描述语言，所以面向对象部分都是 interface ，在 ets 侧，会默认生成 `interface CreditCard` 以及 `class CreditCard_inner implements CreditCard` 使用 `@class` 可以在ets侧直接生成 `class CreditCard`

`@get` 与 `@set` taihe 作为接口描述语言，并不支持在idl侧定义成员变量，使用 `@get` 与 `@set` 注释的方法在 ets 侧会对应为可读和可写，如样例中的 CreditCard 在 ets 侧会有一个只读变量 balance，以及一个可读写变量 intlEnabled，变量名为函数get set 后面的字符串，然后首字符小写

## 第二步，完成C++实现
```C++
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

## 第三步，在 ets 侧使用
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
card.pay(50.0); // 子类可以直接调用父类inerface的方法
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

在 ets 侧，子类可以直接调用父类interface的方法，但是需要注意的是，在 c++ 侧，如果子类需要调用父类 interface 的方法，则需要手动转换一次

举例如下：
```C++
CreditCard card = makeCreditCard(100.0);
// 如果想要调用 pay 方法，因为 pay 是通过继承得到的，在 C++ 侧需要转换为父类 interface
card.pay(50.0); // false !
Payable(card).pay(50.0); // success !
```