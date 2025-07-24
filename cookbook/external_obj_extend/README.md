# External object extend

前面的章节中，我们讲述了 class 继承 class 的建议写法

本章继续介绍继承外部 class 的建议写法，通过 `@!sts_inject` 注解将 ETS 侧数据结构注入，保证继承关系，定义 C++ 侧数据结构（以 `_inner` 后缀标识）调用具体函数实现。注意， C++ 数据结构（以 `_th` 后缀标识）不能在用户侧使用。

## 第一步：在 Taihe IDL 文件中声明

假设当前文件中定义了一个类 MyContext，需要继承其他文件中定义好的类 Context，类里有两个方法，start() 和 stop()

假设希望覆盖父类的 stop() 方法，使用父类的 start() 方法，则在 Taihe IDL 文件中的定义如下：
```taihe
@!sts_inject("import {Context} from 'other.subsystem';")

// C++ 数据结构，在内部使用
@class
interface MyContext_inner {
    // 此处只需要声明 override 的方法
    stop(): String;
}
// 构造内部对象
function createMyContext_inner(): MyContext_inner;

// ETS 数据结构，保证继承关系
@!sts_inject("
export class MyContext extends Context {
    inner: MyContext_inner;
    // 此处只需要实现 override 的方法
    stop(): string {
        return this.inner.stop();
    }
    constructor() {
        this.inner = createMyContext_inner();
    }
    constructor(arg: MyContext_inner) {
        this.inner = arg;
    }
}
")
```

这里使用到的 Context 类型如下：
```typescript
export class Context {
    start(): string {
        return "Context start";
    }
    stop(): string {
        return "Context stop";
    }
}
```

## 第二步：实现声明的接口

```C++
class MyContext_innerImpl {
public:
    MyContext_innerImpl() {}

    ::taihe::string start() {
        return "MyContext start";
    }
    ::taihe::string stop() {
        return "MyContext stop";
    }
};

::external_obj_extend::MyContext_inner createMyContext_inner() {
    return taihe::make_holder<MyContext_innerImpl, ::external_obj_extend::MyContext_inner>();
}
```

在 C++ 侧实现类中的方法并提供构造函数

## 第三步：生成并编译

用户侧使用

`main.ets`
```TypeScript
let context = new Context();
console.log("base class: ", context.start(), " ", context.stop());
let mycontext = new lib.MyContext();
console.log("sub class: ", mycontext.start(), " ", mycontext.stop());
```

Output:
```sh
base class:  Context start   Context stop
sub class:  Context start   MyContext stop
```
