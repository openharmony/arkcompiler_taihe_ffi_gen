# ArrayBuffer

> **学习目标**：掌握 Taihe 中 ArrayBuffer 类型的定义与使用。

## 核心概念

| Taihe 表示 | ArkTS 类型 | C++ 类型 |
|------------|------------|----------|
| `@arraybuffer Array<u8>` | `ArrayBuffer` | `array_view<uint8_t>` |

> **注意**：`@arraybuffer` 注解只能用于 `Array<u8>` 类型。

---

## 第一步：定义接口

**File: `idl/arraybuffer.taihe`**

```rust
function convert2Int(a: @arraybuffer Array<u8>): i32;
```

## 第二步：实现 C++ 代码

**File: `author/src/arraybuffer.impl.cpp`**

```cpp
#include "arraybuffer.impl.hpp"

using namespace taihe;

// 将字节数组转换为 int32
int32_t convert2Int(array_view<uint8_t> a) {
    if (a.size() < 4) {
        set_business_error(1, "ArrayBuffer len < 4");
        return 0;
    }
    return *reinterpret_cast<const int32_t*>(a.begin());
}

TH_EXPORT_CPP_API_convert2Int(convert2Int);
```

> **说明**：在 C++ 侧，ArrayBuffer 的使用方式与普通 `Array<T>` 相同，区别仅在于 ArkTS 侧对应 `ArrayBuffer` 类型。

## 第三步：编译运行

```sh
taihe-tryit test -u sts cookbook/arraybuffer -Carkts:keep-name
```

## 使用示例

**File: `user/main.ets`**

```typescript
import * as other_type from "arraybuffer";

loadLibrary("arraybuffer");

function main() {
    // 创建 ArrayBuffer 并填充数据
    let data: byte[] = [1, 1, 0, 0];  // 小端序：0x00000101 = 257
    let buffer = new ArrayBuffer(data.length);
    for (let i = 0; i < data.length; i++) {
        buffer.set(i, data[i]);
    }
    
    let num = other_type.convert2Int(buffer);
    console.log("num: " + num);  // num: 257
}
```

**输出：**

```
num: 257
```

---

## 相关文档

- [TypedArray](../typedarray/README.md) - TypedArray 类型
- [基础类型](../basic_abilities/README.md) - 基本类型映射
