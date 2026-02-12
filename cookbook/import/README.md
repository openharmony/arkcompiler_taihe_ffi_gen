# Import 导入

> **学习目标**：掌握如何在 Taihe 中导入和使用其他模块。

本教程以"用户通知系统"为例，介绍 Taihe 的模块导入机制。

## 导入语法

Taihe 支持两种导入方式：

| 语法 | 说明 | 示例 |
|------|------|------|
| `from A use B;` | 从包 A 导入声明 B | `from user use IUser;` |
| `use A;` | 导入整个包 A | `use user;` |

### 别名语法

为避免命名冲突，可以使用 `as` 关键字：

```rust
use user as u;                    // 包别名
from user use IUser as UserType;  // 声明别名
```

---

## 第一步：定义模块

**File: `idl/user.taihe`**

```rust
interface IUser {
    @get getEmail(): String;
    @set setEmail(email: String): void;
}

function makeUser(email: String): IUser;
```

**File: `idl/notification.taihe`**

```rust
// 方式一：导入单个声明
from user use IUser;

interface INotificationService {
    sendMessage(user: IUser): void;
}

function makeNotificationService(): INotificationService;
```

或者使用整包导入：

```rust
// 方式二：导入整个包
use user;

interface INotificationService {
    sendMessage(u: user.IUser): void;  // 需要使用 包名.类型 的形式
}

function makeNotificationService(): INotificationService;
```

## 第二步：实现 C++ 代码

**File: `author/src/user.impl.cpp`**

```cpp
#include "user.impl.hpp"

using namespace taihe;

class IUserImpl {
public:
    IUserImpl(string_view email) : m_email(email) {}

    string getEmail() {
        return m_email;
    }

    void setEmail(string_view email) {
        m_email = email;
    }

private:
    string m_email;
};

IUser makeUser(string_view email) {
    return make_holder<IUserImpl, IUser>(email);
}

TH_EXPORT_CPP_API_makeUser(makeUser);
```

**File: `author/src/notification.impl.cpp`**

```cpp
#include "notification.impl.hpp"
#include "user.proj.hpp"

using namespace taihe;

class INotificationServiceImpl {
public:
    void sendMessage(::user::weak::IUser user) {
        std::cout << "Welcome " << user->getEmail() << std::endl;
    }
};

INotificationService makeNotificationService() {
    return make_holder<INotificationServiceImpl, INotificationService>();
}

TH_EXPORT_CPP_API_makeNotificationService(makeNotificationService);
```

## 第三步：编译运行

```sh
taihe-tryit test -u sts cookbook/notification
```

## 使用示例

**File: `user/main.ets`**

```typescript
import * as user from "user";
import * as notification from "notification";

loadLibrary("notification");

function main() {
    let userA = user.makeUser("alice@example.com");
    let userB = user.makeUser("bob@example.com");
    
    let service = notification.makeNotificationService();
    service.sendMessage(userA);
    service.sendMessage(userB);
}
```

**输出：**

```
Welcome alice@example.com
Welcome bob@example.com
```

---

## 相关文档

- [Interface 接口](../interface/README.md) - 接口定义与实现
- [继承](../inherit/README.md) - 接口继承
