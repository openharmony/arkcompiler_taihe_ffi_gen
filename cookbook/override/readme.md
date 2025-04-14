# 重写

重写(override)是指在子类中重新定义父类中已存在的方法，以改变其行为。在运行时，系统会根据对象的实际类型自动调用对应版本的方法。

taihe支持用户在sts侧创建子类，继承在taihe文件中声明的父类，并重写其方法。

## 第一步 在taihe文件中声明

`override/idl/override.taihe`

```taihe
@class
interface UIAbility {
    onForeground(): void;
    onBackground(): void;
}

@ctor("UIAbility")
function getUIAbility(): UIAbility;

function useUIAbility(a: UIAbility): void;

@static("UIAbility")
function logLifecycle(str: String): void;
```

这里涉及3种注解：`@class` `@ctor` `@static`

- `@class`

  对于上面的接口声明，如果不添加 `@class` 注解，那么在 ets 侧会默认投影成 `interface UIAbility`. 如果需要将其投影为 `class` 则需使用 `@class` 注解，使其在 ets 侧直接生成为 `class CUIAbility`.

- `@ctor`
  该注解会给对应的 class 添加构造器，仅对 `@class` 注解的 interface 有效

- `@static`
  该注解会给对应的 class 添加静态方法，仅对 `@class` 注解的 interface 有效

## 第二步 实现声明的接口

`useUIAbility`函数接收`UIAbility`类型的参数，根据传入参数对象的实际类型调用`onForeground`方法和`onBackground`方法。

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

`compiler/`
```sh
./run-test /path/to/override -ani
```

用户侧创建类`MyAbility`继承了taihe文件中声明的类`UIAbility`，并重写了方法`onForeground`，创建了一个`MyAbility`类的实例，并将其赋值给类型为`UIAbility`的变量，以此做为参数传入`useUIAbility`函数。

可以看出实际上在C++侧调用了sts侧重写的`onForeground`方法和C++侧原本的`onBackground`方法。

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