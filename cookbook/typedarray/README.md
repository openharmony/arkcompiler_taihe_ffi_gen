# TypedArray

Taihe 支持 TS 语言中的 TypedArray 类型，如 Uint8Array, Int8Array 等，其对应的注解为在相应的 `Array<T>` 上添加注解 `@typedarray`，例如，`Uint8Array` 在 Taihe 中表示为 `@typedarray Array<u8>`，`Int8Array` 表示为 `@typedarray Array<i8>`。

## 第一步：编写接口原型

**File: `idl/typedarray.taihe`**
```taihe
function createUint16Array(): @typedarray Array<u16>;
function printUint16Array(arr: @typedarray Array<u16>): void;
```

## 第二步：完成 C++ 实现

**File: `author/src/typedarray.impl.cpp`**
```c++
array<uint16_t> createUint16Array() {
    return {1, 3, 5, 6, 9};
}

void printUint16Array(array_view<uint16_t> arr) {
    size_t i = 0;
    for (uint16_t val : arr) {
        std::cout << "Index: " << i++ << " Value: " << val << std::endl;
    }
}
```

## 第三步：在 ets 侧使用

```typescript
// ets 侧创建，C++ 侧调用
let arrbuf = new ArrayBuffer(8);
arrbuf.set(0, 0xff as byte);
arrbuf.set(1, 0xff as byte);
arrbuf.set(2, 0x01 as byte);
arrbuf.set(3, 0x00 as byte);
let ets_uarr = new Uint16Array(arrbuf, 0, 2);
typearr.printUint16Array(ets_uarr);

// C++ 侧创建，ets 侧调用
let c_uarr = typearr.createUint16Array();
console.log(c_uarr);
```

Output:
```sh
Index: 0 Value: 65535
Index: 1 Value: 1
1,3,5,6,9
```