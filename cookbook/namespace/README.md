# Namespace

taihe 使用注解的方式实现 sts 的 namespace, 注解为 `@!namespace()`, 下面是使用示例：

## 第一步：编写接口原型

**File: `idl/module1.taihe`**
```rust
function module1Run(): void;
```

**File: `idl/module1.foo.taihe`**
```rust
@!namespace("module1", "foo")

function fooFunc(): void;
```

**File: `idl/module2.bar.taihe`**
```rust
@!namespace("module2", "bar")

function barFunc(): void;
```

首先，我们推荐 Taihe IDL 文件的命名为 <module_name>.<namespace_name>.taihe

上面的例子中，mudule1 与 module2 为 2 个模块，foo 是 module1 的一个命名空间，bar 是 module2 的一个命名空间

命名空间的语法为 `@!namespace(<mudule_name>, <namespace_name>)`, 表示该文件下面的内容为 `<module_name>` 模块下，   `<namespace_name>` 命名空间中的内容

此外，我们可以发现，可以直接写 module2.bar.taihe 的内容，而不需要一个空的 module2.Taihe IDL 文件，给用户使用提供一定的便利

## 第二步：实现声明的接口

**File: `author/src/module1.impl.cpp`**
```cpp
void module1Run() {
    std::cout << "Module: module1" << std::endl;
}
```

**File: `author/src/module1.foo.impl.cpp`**
```cpp
void fooFunc() {
    std::cout << "namespace: module1.foo, func: foo" << std::endl;
}
```

**File: `author/src/module2.bar.impl.cpp`**
```cpp
void barFunc() {
    std::cout << "namespace: module2.bar, func: bar" << std::endl;
}
```

## 第三步：在 ets 侧使用

```typescript
Module1.module1Run();
Module1.foo.fooFunc();
Module2.bar.barFunc();
```

Output:
```sh
Module: module1
namespace: module1.foo, func: foo
namespace: module2.bar, func: bar
```