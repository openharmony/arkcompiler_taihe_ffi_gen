# TypedArray

> **学习目标**：掌握 Taihe 中 TypedArray 类型的定义与使用。

## 核心概念

Taihe 通过 `@typedarray` 注解支持 ArkTS 的数组类型。

### @typedarray 映射

| Taihe 表示 | ArkTS 类型 | C++ 类型 |
|------------|------------|----------|
| `@typedarray Array<u8>` | `Uint8Array` | `array<uint8_t>` |
| `@typedarray Array<i8>` | `Int8Array` | `array<int8_t>` |
| `@typedarray Array<u16>` | `Uint16Array` | `array<uint16_t>` |
| `@typedarray Array<i16>` | `Int16Array` | `array<int16_t>` |
| `@typedarray Array<u32>` | `Uint32Array` | `array<uint32_t>` |
| `@typedarray Array<i32>` | `Int32Array` | `array<int32_t>` |
| `@typedarray Array<f32>` | `Float32Array` | `array<float>` |
| `@typedarray Array<f64>` | `Float64Array` | `array<double>` |

---

## TypedArray 示例

### 第一步：定义接口

**File: `idl/typedarray.taihe`**

```rust
function createUint16Array(): @typedarray Array<u16>;
function printUint16Array(arr: @typedarray Array<u16>): void;
```

### 第二步：实现 C++ 代码

**File: `author/src/typedarray.impl.cpp`**

```cpp
#include "typedarray.impl.hpp"

using namespace taihe;

array<uint16_t> createUint16Array() {
    return {1, 3, 5, 6, 9};
}

void printUint16Array(array_view<uint16_t> arr) {
    size_t i = 0;
    for (uint16_t val : arr) {
        std::cout << "Index: " << i++ << " Value: " << val << std::endl;
    }
}

TH_EXPORT_CPP_API_createUint16Array(createUint16Array);
TH_EXPORT_CPP_API_printUint16Array(printUint16Array);
```

---

## 编译运行

```sh
taihe-tryit test -u sts cookbook/typedarray
```

## 使用示例

**File: `user/main.ets`**

```typescript
import * as typearr from "typedarray";

loadLibrary("typedarray");

function main() {
    // TypedArray: ArkTS 侧创建，C++ 侧使用
    let buffer = new ArrayBuffer(4);
    buffer.set(0, 0xff as byte);  // 低字节
    buffer.set(1, 0xff as byte);  // 高字节 -> 0xffff = 65535
    buffer.set(2, 0x01 as byte);
    buffer.set(3, 0x00 as byte);  // -> 0x0001 = 1
    
    let etsArray = new Uint16Array(buffer, 0, 2);
    typearr.printUint16Array(etsArray);
    
    // TypedArray: C++ 侧创建，ArkTS 侧使用
    let cppArray = typearr.createUint16Array();
    console.log(cppArray);
}
```

**输出：**

```
Index: 0 Value: 65535
Index: 1 Value: 1
1,3,5,6,9
```

---

## 相关文档

- [ArrayBuffer](../arraybuffer/README.md) - ArrayBuffer 类型
- [BigInt](../bigint/README.md) - BigInt 类型
- [基础类型](../basic_abilities/README.md) - 基本类型映射
