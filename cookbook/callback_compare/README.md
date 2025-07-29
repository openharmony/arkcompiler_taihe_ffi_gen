# Callback 对象比较

目前 taihe 已支持 callback 对象的判等比较

## 第一步：编写接口原型

我们写一个函数，输入是两个 callback, 输出结果是比较两个 callback 是否是相等，如果相等返回 true，否则返回 false

**File: `idl/cb_compare.taihe`**
```rust
function cbCompare(cb1: () => String, cb2: () => String): bool;
```

## 第二步：完成 C++ 实现

**File: `author/src/cb_compare.impl.cpp`**
```cpp
bool cbCompare(::taihe::callback_view<::taihe::string()> cb1, ::taihe::callback_view<::taihe::string()> cb2) {
    return cb1 == cb2 ? true : false;
}
```

C++ 侧支持使用 `==` 来比较两个 callback

## 第三步：在 ets 侧使用

```typescript
// 定义两个 callback
let callback_1 = () => {
    console.log("Callback 1 executed");
    return "Callback 1 result";
};
let callback_2 = () => {
    console.log("Callback 2 executed");
    return "Callback 2 result";
};
// 使用函数进行比较
console.log("same callback: " + cbCompare(callback_1, callback_1))
console.log("different callback: " + cbCompare(callback_1, callback_2))
```

Output：
```sh
same callback: true
different callback: false
```