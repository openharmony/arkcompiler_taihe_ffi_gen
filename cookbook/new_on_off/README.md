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
```rust
interface ISetterObserver {
    @rename("on")
    onSet(type: String, a: () => void): void;

    @rename("off")
    offSet(type: String, a: () => void): void;
}

function getISetterObserver(): ISetterObserver;

@static_overload("on")
function onFoo(type: String, a: () => void): void;

@static_overload("on")
function onBar(type: String, a: () => void): void;

@static_overload("on")
function onBaz(type: String, a: i32, cb: (b: i32) => void): void;

@static_overload("off")
function offFoo(type: String, a: () => void): void;

@static_overload("off")
function offBar(type: String, a: () => void): void;

@static_overload("off")
function offBaz(type: String, a: i32, cb: (b: i32) => void): void;
```

on/off 函数在支持了 java like 重载后，使用 `@rename` 和 `@static_overload` 注解来实现。

@rename注解参考[文档](../rename_example/README.md)

@static_overload注解参考[文档](../javalike_overload/README.md)

## 第二步：完成 C++ 实现

**File: `author/src/on_off.impl.cpp`**
```cpp
class ISetterObserverImpl {
public:
  ISetterObserverImpl() {}

  void onSet(::taihe::string_view type, callback_view<void()> a) {
    a();
    std::cout << "IBase::onSet" << std::endl;
  }

  void offSet(::taihe::string_view type, callback_view<void()> a) {
    a();
    std::cout << "IBase::offSet" << std::endl;
  }
};

ISetterObserver getISetterObserver() {
  return make_holder<ISetterObserverImpl, ISetterObserver>();
}

void onFoo(::taihe::string_view type, callback_view<void()> a) {
  a();
  std::cout << "onFoo" << std::endl;
}

void onBar(::taihe::string_view type, callback_view<void()> a) {
    a();
    std::cout << "onBar" << std::endl;
}

void onBaz(::taihe::string_view type, int32_t a, callback_view<void(int32_t)> cb) {
    cb(a);
    std::cout << "onNewBaz" << std::endl;
}

void offFoo(::taihe::string_view type, callback_view<void()> a) {
    a();
    std::cout << "offFoo" << std::endl;
}

void offBar(::taihe::string_view type, callback_view<void()> a) {
    a();
    std::cout << "offBar" << std::endl;
}

void offBaz(::taihe::string_view type, int32_t a, callback_view<void(int32_t)> cb) {
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
onFoo
onNewBaz callback, num: 1
onNewBaz
offFoo callback
offFoo
offBar callback
offFoo
offNewBaz callback, num: 0
offNewBaz
```