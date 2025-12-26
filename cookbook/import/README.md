# 导入

我们经常会需要将一个模块导入到另一个模块，本章节已**用户注册通知**为例，介绍 taihe 的 import

## 第一步：编写接口原型

**File: `idl/user.taihe`**

```rust
interface IUser {
    @get getEmail(): String;
    @set setEmail(path: String): void;
}

function makeUser(path: String): IUser;
```

**File: `idl/notification.taihe`**

```rust
from user use IUser;

interface INotificationService{
    sendMessage(a: IUser): void;
}

function makeNotificationService(): INotificationService;
```

taihe 有两种导入方式：

1. `from A use B;`
2. `use A;`

其中，A 为 taihe 的 pkg，B 为声明

本章样例使用 `from user use IUser`，即从 `user` 包里导入 `IUser`

当然也可以使用 `use user` 来导入整个 `user.taihe` 文件，但是这样做的话，在被导入的 Taihe IDL 文件 `notification.taihe` 里，使用导入的模块则需要前面跟上 pkg 名

```rust
use user;

interface INotificationService{
    sendMessage(a: user.IUser): void; // 此处使用 pkg.module 的形式
}

function makeNotificationService(): INotificationService;
```

为了避免重名的情况，支持 `as` 语法：

1. `use A as C;`

2. `from A use B as C;`

## 第二步：完成 C++ 实现

**File: `author/src/user.impl.cpp`**

```cpp
class IUserImpl {
public:
    IUserImpl(string_view path): m_email(path){}

    string getEmail() {
        return this->m_email;
    }

    void setEmail(string_view path) {
        this->m_email = path;
    }

private:
    string m_email;
};

IUser makeUser(string_view path) {
    return make_holder<IUserImpl, IUser>(path);
}
```

**File: `author/src/ntification.impl.cpp`**

```cpp
class INotificationServiceImpl {
public:
    INotificationServiceImpl() {}

    void sendMessage(::user::weak::IUser a) {
        string_view user_email = a->getEmail(); // 使用 -> 调用方法
        std::cout << "Welcome " << a->getEmail() << std::endl;
    }
};

INotificationService makeNotificationService() {
    return make_holder<INotificationServiceImpl, INotificationService>();
}
```

此处有一个需要注意的地方在于在 C++ 侧调用 taihe interface 的方法，当需要调用 taihe interface 的方法时，在 c++ 侧调用方法时，需要使用 `->` 的方式调用函数，而非 `.` 的方式

```cpp
a.getEmail();  // error!
a->getEmail(); // success!
```

## 第三步：在 ets 侧使用

**File: `user/main.ets`**

```typescript
let userA = user.makeUser("12345@huawei.com");
let userB = user.makeUser("67890@outlook.com");
let noter = notification.makeNotificationService();
noter.sendMessage(userA);
noter.sendMessage(userB);
```

**Stdout**

```sh
Welcome 12345@huawei.com
Welcome 67890@outlook.com
```
