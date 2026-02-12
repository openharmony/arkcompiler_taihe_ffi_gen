# Export Default

> **学习目标**：掌握如何使用 `@sts_export_default` 注解实现 ArkTS 的 export default。

## 核心概念

| 注解 | 作用 |
|------|------|
| `@!sts_export_default` | 为当前文件/命名空间添加 export default |
| `@sts_export_default` | 为接口/枚举/联合类型添加 export default |

> **注意**：ArkTS 只允许对一个实体使用 export default，请勿在同一个包内多次使用。

---

## 第一步：定义接口

**File: `idl/export_example.taihe`**

```rust
@!namespace("export_pkg", "export_ns")
@!sts_export_default

struct Inner {
    i: i32;
    s: String;
}
```

**File: `idl/import_example.taihe`**

```rust
from export_example use Inner;

function testImport(obj: Inner): void;
```

### 使用方式

**方式一：为 namespace 添加 export default**

```rust
@!namespace("xxx", "yyy")
@!sts_export_default
// ...
```

**方式二：为类型添加 export default**

```rust
@sts_export_default
interface IfaceA {}
```

## 第二步：生成的代码

**File (Generated): `generated/export_pkg.ets`**

```typescript
export default namespace export_ns {
    export interface Inner {
        i: int;
        s: string;
    }
    // ...
}
```

## 第三步：实现 C++ 代码

**File: `author/src/import_example.impl.cpp`**

```cpp
#include "import_example.impl.hpp"

using namespace taihe;

void testImport(export_example::Inner const& obj) {
    std::cout << "obj.s = " << obj.s << ", obj.i = " << obj.i << std::endl;
}

TH_EXPORT_CPP_API_testImport(testImport);
```

## 第四步：编译运行

```sh
taihe-tryit test -u sts cookbook/export_default
```

## 使用示例

**File: `user/main.ets`**

```typescript
// 导入 export default 使用 import X from "Y"
// 不能使用 import * as X from "Y"
import export_ns from "export_pkg";
import { testImport } from "import_example";

loadLibrary("export_default");

function main() {
    let obj: export_ns.Inner = { i: 1, s: "str" };
    testImport(obj);
}
```

**输出：**

```
obj.s = str, obj.i = 1
```

---

## 相关文档

- [Namespace 命名空间](../namespace/README.md) - 命名空间用法
- [Import 导入](../import/README.md) - 模块导入
