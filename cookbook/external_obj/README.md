# External Object（外部对象）

> **学习目标**：掌握如何在 C++ 实现中处理 ArkTS 侧的外部对象。

本教程介绍 `Opaque` 类型和 ANI Runtime 的使用。

## 核心概念

| 类型/注解 | 作用 | 说明 |
|-----------|------|------|
| `Opaque` | 不透明指针类型 | 在 C++ 侧表示为 `uintptr_t` |
| `@sts_type("T")` | 指定 ArkTS 类型 | 将 Opaque 在 ArkTS 侧映射为指定类型 |
| `@sts_inject("...")` | 注入代码 | 在生成的 ArkTS 文件中插入代码 |

### 类型映射

| Taihe 类型 | C++ 类型 | 说明 |
|------------|----------|------|
| `Opaque` | `uintptr_t` | 可以 cast 为任意 ANI 对象指针 |

---

## 第一步：定义接口

**File: `idl/external_obj.taihe`**

```rust
// 注入 import 语句到生成的 ArkTS 文件
@!sts_inject("import {Person} from 'other.subsystem';")

function is_string(s: Opaque): bool;
function get_objects(): Array<Opaque>;

// 使用 @sts_type 指定 Opaque 在 ArkTS 侧的具体类型
function processPerson(person: @sts_type("Person") Opaque): void;
```

**ArkTS 侧的 Person 类型定义：**

```typescript
export interface Person {
    name: string;
    age: number;
}
```

### 注解说明

| 注解 | 用法 |
|------|------|
| `@!sts_inject("...")` | 在文件级别注入代码（注意 `!` 表示作用于当前文件） |
| `@sts_type("Type")` | 放在 `Opaque` 类型前，指定 ArkTS 侧的具体类型 |

## 第二步：实现 C++ 代码

**File: `author/src/external_obj.impl.cpp`**

```cpp
#include "external_obj.impl.hpp"
#include "taihe/runtime.hpp"  // ANI Runtime 支持

using namespace taihe;

// 判断外部对象是否为 string 类型
bool is_string(uintptr_t obj) {
    ani_env* env = get_env();  // 获取当前 ANI 环境
    ani_boolean result;
    ani_class cls;
    
    env->FindClass("std.core.String", &cls);
    env->Object_InstanceOf((ani_object)obj, cls, &result);
    
    return result;
}

// 返回包含 ANI 对象的数组
array<uintptr_t> get_objects() {
    ani_env* env = get_env();
    
    // 创建字符串对象
    ani_string str;
    env->String_NewUTF8("AAA", 3, &str);
    
    // 获取 undefined
    ani_ref undef;
    env->GetUndefined(&undef);
    
    return array<uintptr_t>({(uintptr_t)str, (uintptr_t)undef});
}

// 处理 Person 对象
void processPerson(uintptr_t person) {
    ani_env* env = get_env();
    ani_object obj = reinterpret_cast<ani_object>(person);
    
    // 获取 name 属性
    ani_string name;
    env->Object_GetPropertyByName_Ref(obj, "name", 
                                       reinterpret_cast<ani_ref*>(&name));
    
    // 获取 age 属性
    ani_int age;
    env->Object_GetPropertyByName_Int(obj, "age", &age);
    
    // 转换字符串
    ani_size len;
    env->String_GetUTF8Size(name, &len);
    char* name_utf8 = new char[len + 1];
    env->String_GetUTF8(name, name_utf8, len + 1, &len);
    
    std::cout << "name: " << name_utf8 << ", age: " << age << std::endl;
    
    delete[] name_utf8;
}

TH_EXPORT_CPP_API_is_string(is_string);
TH_EXPORT_CPP_API_get_objects(get_objects);
TH_EXPORT_CPP_API_processPerson(processPerson);
```

### ANI Runtime 要点

| 函数 | 作用 |
|------|------|
| `get_env()` | 获取当前 ANI 环境指针 |
| `env->FindClass(name, &cls)` | 查找类 |
| `env->Object_InstanceOf(obj, cls, &result)` | 类型检查 |
| `env->String_NewUTF8(str, len, &result)` | 创建字符串 |
| `env->GetUndefined(&ref)` | 获取 undefined 值 |

> **注意**：与 ANI 原生函数不同，Taihe 函数没有 `env` 参数，需要通过 `get_env()` 获取。

## 第三步：编译运行

```sh
taihe-tryit test -u sts cookbook/external_obj -Csts:keep-name
```

## 使用示例

**File: `user/main.ets`**

```typescript
import * as extobj from "external_obj";
import { Person } from "other.subsystem";

loadLibrary("external_obj");

function main() {
    // 检测类型
    console.log(extobj.is_string("hello"));  // true
    console.log(extobj.is_string(123));      // false
    
    // 处理外部对象
    let person: Person = { name: "John", age: 30 };
    extobj.processPerson(person);
    
    // 获取对象数组
    console.log(extobj.get_objects());
}
```

**输出：**

```
true
false
name: John, age: 30
[AAA, undefined]
```

---

## 相关文档

- [Interface 接口](../interface/README.md) - 接口定义
- [基础类型](../basic_abilities/README.md) - 类型映射
