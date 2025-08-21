# Rename

用户可以使用 `@rename` 注解修改 ets 侧的函数名


## 第一步：在 Taihe IDL 文件中声明

`rename_example/idl/rename_example.taihe`
```rust
@rename("newFoo")
function oldFoo(a: i32, b: i32): i32;
```

当用户对函数使用了 `@rename` 注解，会使得生成 ets 代码的 export 的函数名修改为新名字

```typescript
// 不使用 @rename
native function _taihe_oldFoo_native(a: int, b: int): int;
export function oldFoo(a: int, b: int): int {
    return _taihe_oldFoo_native(a, b);
}
function _taihe_oldFoo_reverse(a: int, b: int): int {
    return oldFoo(a, b);
}
// 使用 @rename
native function _taihe_oldFoo_native(a: int, b: int): int;
export function newFoo(a: int, b: int): int {
    return _taihe_oldFoo_native(a, b);
}
function _taihe_oldFoo_reverse(a: int, b: int): int {
    return newFoo(a, b);
}
```

## 第二步：实现声明的接口

`rename_example/author/src/rename_example.impl.cpp`
```cpp
int32_t oldFoo(int32_t a, int32_t b) {
    return a + b;
}
```

## 第三步：生成并编译

```sh
taihe-tryit test -u sts cookbook/rename_example -Csts:keep-name
```

`main.ets`
```typescript
let res = rename_example.newFoo(1, 2);
console.log("res = " + res);
```

输出：
```sh
res = 3
```