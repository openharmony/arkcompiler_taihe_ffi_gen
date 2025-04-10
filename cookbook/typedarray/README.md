# TypedArray

Taihe 可以使用注解的方式来使用 typed array 注解为 `@!typed_array`

## 第一步：编写接口原型

**File: `idl/typedarray.taihe`**
```taihe
@!typed_array

function createUint16Array(): Array<u16>;
function printUint16Array(arr: Array<u16>): void;
```

目前该注解只能作用于太和文件，使用该注解后，taihe所有的 Array\<ux\>都会对接为 TypedArray

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
// ets侧创建, c++侧调用
let arrbuf = new ArrayBuffer(8);
arrbuf.set(0, 0xff as byte);
arrbuf.set(1, 0xff as byte);
arrbuf.set(2, 0x01 as byte);
arrbuf.set(3, 0x00 as byte);
let ets_uarr = new Uint16Array(arrbuf, 0, 2);
typearr.printUint16Array(ets_uarr);

// C++侧创建，ets侧调用
let c_uarr = typearr.createUint16Array();
console.log(c_uarr);
```

Output:
```sh
Index: 0 Value: 65535
Index: 1 Value: 1
1,3,5,6,9
```