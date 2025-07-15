# 重写

重写（override）是指在子类中重新定义父类中已存在的方法，以改变其行为。在运行时，系统会根据对象的实际类型自动调用对应版本的方法。

taihe 支持用户在 sts 侧创建子类，继承在 taihe 文件中声明的父类，并重写其方法。

## 第一步 在 taihe 文件中声明

`override/idl/override.taihe`

```taihe
@class
interface UIAbility {
    onForeground(): void;
    onBackground(): void;
}

@rename @constructor("UIAbility")
function getUIAbility(): UIAbility;

function useUIAbility(a: UIAbility): void;

@static("UIAbility")
function logLifecycle(str: String): void;
```

这里涉及 3 种注解：`@class` `@constructor` `@static` `@rename`

- `@class`

  对于上面的接口声明，如果不添加 `@class` 注解，那么在 ets 侧会默认投影成 `interface UIAbility`. 如果需要将其投影为 `class` 则需使用 `@class` 注解，使其在 ets 侧直接生成为 `class CUIAbility`.

- `@constructor`
  该注解会给对应的 class 添加构造器，仅对 `@class` 注解的 interface 有效

- `@static`
  该注解会给对应的 class 添加静态方法，仅对 `@class` 注解的 interface 有效

- `@rename`
  该注解会改变 ets 侧方法名，使用 `@rename("<new_name>")` 会使得 ets 侧方法名修改为 `new_name`, 不带参数时适用于匿名函数

注：根据 ets 规范，当一个 class 只有一个构造函数时，该函数应该为匿名构造函数，所以应该使用 `@rename`

```taihe
@class
interface IfaceA {

}

@rename @constructor("IfaceA")
function createIfaceA(): IfaceA;
```

注：根据 ets 新重载规则，当一个 class 有多个构造函数时，需要使用 `@static_overload`

```taihe
@class
interface IfaceB {

}

@static_overload @constructor("IfaceB")
function createIfaceBWithInt(arg: i32): IfaceB;

@static_overload @constructor("IfaceB")
function createIfaceBWithString(arg: String): IfaceB;
```

## 第二步 实现声明的接口

`useUIAbility` 函数接收 `UIAbility` 类型的参数，根据传入参数对象的实际类型调用 `onForeground` 方法和 `onBackground` 方法。

`override/author/src/override.impl.cpp`

```C++
class UIAbility {
public:
    void onForeground() {
        std::cout << "in cpp onForeground" << std::endl;
    }
    void onBackground() {
        std::cout << "in cpp onBackground" << std::endl;
    }
};
::override::UIAbility getUIAbility() {
    return make_holder<UIAbility, ::override::UIAbility>();
}
void useUIAbility(::override::weak::UIAbility a) {
    a->onForeground();
    a->onBackground();
}
void logLifecycle(string_view str) {
  std::cout << "[UIAbility]: " << str << std::endl;
}
```

## 第三步 生成并编译

```sh
# 注：taihe 文件里的函数与 C++ 规范一致，所以函数会在生成的 ets 侧自动转变为小写字母开头函数
# taihe 文件中的写法：
#   function FooBar(): void;
# 生成的 ets 侧代码
#   function fooBar(): void;
# 如果希望生成的 ets 侧函数与 taihe 文件一致，可以使用 --sts-keep-name
taihe-tryit test -u sts path/to/override --sts-keep-name
```

用户侧创建类 `MyAbility` 继承了 taihe 文件中声明的类 `UIAbility`，并重写了方法 `onForeground`，创建了一个 `MyAbility` 类的实例，并将其赋值给类型为 `UIAbility` 的变量，以此做为参数传入 `useUIAbility` 函数。

可以看出实际上在 C++ 侧调用了 sts 侧重写的 `onForeground` 方法和 C++ 侧原本的 `onBackground` 方法。

`main.ets`
```TypeScript
class MyAbility extends UIAbility {
    constructor () {
        super();
    }
    onForeground(): void {
        console.log("in ets onForeground")
    }
}
let my_uiability: UIAbility = new MyAbility();
useUIAbility(my_uiability);
MyAbility.logLifecycle("using uiability")
```

上面的 ets 侧代码使用 MyAbility 继承 UIAbility

```sh
in ets onForeground
in cpp onBackground
[UIAbility]: using uiability
```