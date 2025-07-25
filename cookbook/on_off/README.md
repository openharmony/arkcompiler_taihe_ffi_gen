# On 与 Off

在 sts 中有些接口形如：

```typescript
on(target: "foo", callback: (): void);
on(target: "bar", callback: (): void);

off(target: "foo", callback: (): void);
off(target: "bar", callback: (): void);
```

可以使用 taihe 的 `@on_off` 注解

## 第一步：编写接口原型

**File: `idl/on_off.taihe`**
```taihe
interface ISetterObserver {
    @on_off
    onSet(a: () => void): void;

    @on_off
    offSet(a: () => void): void;
}

function getISetterObserver(): ISetterObserver;

@on_off
function onFoo(a: () => void): void;

@on_off
function onBar(a: () => void): void;

@on_off("newBaz")
function onBaz(a: i32, cb: (b: i32) => void): void;

@on_off
function offFoo(a: () => void): void;

@on_off
function offBar(a: () => void): void;

@on_off("newBaz")
function offBaz(a: i32, cb: (b: i32) => void): void;
```

`@on_off` 注解有两种写法

on / off 函数在太和中需要命名形如为 `OnFoo`、`OnBar` 的函数

1. @on_off

    使用第一种写法时，会将 taihe 函数名 on / off 后的字符串作为 sts 侧的 on / off 函数的 target (首字母会自动小写)，如 taihe 函数 OnFoo，在 sts 侧时 target 为 foo

2. @on_off("\<target\>")

    使用第二种写法时，会将 `@on_off("<target>")` 注解中的 \<target\> 作为 sts 侧的 target，如 `@on_off("newBaz") function OnBaz()` 在 sts 侧时 target 为 newBaz

我们推荐使用第二种写法避免因某些函数写法的原因导致的问题

## 第二步：完成 C++ 实现

**File: `author/src/on_off.impl.cpp`**

```C++
class ISetterObserverImpl {
public:
  ISetterObserverImpl() {}

  void onSet(callback_view<void()> a) {
    a();
    std::cout << "IBase::onSet" << std::endl;
  }

  void offSet(callback_view<void()> a) {
    a();
    std::cout << "IBase::offSet" << std::endl;
  }
};

ISetterObserver getISetterObserver() {
  return make_holder<ISetterObserverImpl, ISetterObserver>();
}

void onFoo(callback_view<void()> a) {
  a();
  std::cout << "onFoo" << std::endl;
}

void onBar(callback_view<void()> a) {
    a();
    std::cout << "onBar" << std::endl;
}

void onBaz(int32_t a, callback_view<void(int32_t)> cb) {
    cb(a);
    std::cout << "onNewBaz" << std::endl;
}

void offFoo(callback_view<void()> a) {
    a();
    std::cout << "offFoo" << std::endl;
}

void offBar(callback_view<void()> a) {
    a();
    std::cout << "offBar" << std::endl;
}

void offBaz(int32_t a, callback_view<void(int32_t)> cb) {
    cb(a);
    std::cout << "offNewBaz" << std::endl;
}
```

## 第三步：在 ets 侧使用
```typescript
let num0: Int = 0;
let num1: Int = 1;
let obj = OnOff.getISetterObserver();
obj.on("set", (): void => { console.log("ISetterObserver onSet callback"); });
obj.off("set", (): void => { console.log("ISetterObserver offSet callback"); });
OnOff.on("foo", (): void => { console.log("onFoo callback"); });
OnOff.on("bar", (): void => { console.log("onBar callback"); });
OnOff.on("newBaz", num1, (arg0: Int): void => { console.log("onNewBaz callback, num: " + arg0); });
OnOff.off("foo", (): void => { console.log("offFoo callback"); });
OnOff.off("bar", (): void => { console.log("offBar callback"); });
OnOff.off("newBaz", num0, (arg0: Int): void => { console.log("offNewBaz callback, num: " + arg0); });
```

Output:
```sh
ISetterObserver onSet callback
IBase::onSet
ISetterObserver offSet callback
IBase::offSet
onFoo callback
onFoo
onBar callback
onBar
onNewBaz callback, num: 1
onNewBaz
offFoo callback
offFoo
offBar callback
offBar
offNewBaz callback, num: 0
offNewBaz
```