# 接口合约描述语言

## 包

### 定义包

1. **源文件与包的一一对应**
   - 一个源文件只能描述一个包。
   - 一个包不能分散到多个源文件中。

2. **包名由源文件名唯一确定**
   - 示例：在 `ohos.hardware.sensors.taihe` 文件中，描述了 `ohos.hardware.sensors` 包下的各个成员。

3. **包的成员名称不得与包名相同**
   - 示例：在 `ohos.hardware.sensors` 包下定义 `class SensorManager` 时，不允许定义 `ohos.hardware.sensors.SensorManager.taihe`。
   - 原因：动态语言（如 JS、Python）不支持重名。

### 使用包管理命名空间

1. **默认可直接引用当前包下的名称**
   ```rust
   // example.types.taihe
   struct Foo {}
   struct Bar {}

   function func1(bar: example1.Foo): (); // OK
   function func2(foo: Foo): ();          // OK
   ```

2. **导入其他包并生成别名**
   使用 `use ... as` 或 `from ... use` 为其他包的名称生成别名。
   ```rust
   // example.test1.taihe
   use example.types as myfoo;
   function func3(foo: myfoo.Foo): ();    // OK

   // example.test2.taihe
   from example.types use Bar, Foo as Foobar;
   function func4(foo: Foobar): ();       // OK
   function func5(foo: Bar): ();          // OK
   ```

3. **包间互相隔离，无从属关系**
   ```rust
   // example.taihe
   from types use Foo;            // Error: package `types` does not exist
   use types as mytypes;          // Error: package `types` does not exist
   from example.types use Foo;    // OK
   use example.types;             // OK
   function func6(foo: Foo): ();           // OK
   function func7(foo: example.types.Foo): (); // OK
   ```

## 基础类型

提供以下基础类型：

- **整型**  
  - 无符号：`u8`, `u16`, `u32`, `u64`
  - 有符号：`i8`, `i16`, `i32`, `i64`
- **浮点型**  
  - `f32`, `f64`
- **布尔型**  
  - `bool`
- **字符串类型**  
  - `String`

## 函数

支持在 `class` 或 `interface` 外定义函数。

### 函数参数

函数可拥有任意数量的参数，每个参数由参数名、参数类型和类型修饰符组成。

### 返回值

函数最多只能有一个返回值。若需返回多个值，可以用结构体表示。

合法与非法声明示例：
```rust
function func(m: i32, n: i32): (String, String);  // Error: cannot have multiple return values
struct StringPair {
  a: String;
  b: String;
}
function func(m: i32, n: i32): StringPair;        // OK
function func(foo: String);                       // Error: return type is required
function func(foo: i32): void;                    // OK
```

## 结构体

结构体是数据成员的组合，其成员类型包括基础类型、枚举类型、接口类型和其他结构体类型：
```rust
interface Base {}
struct Foo {
  a: i32;
  s: String;
  i: Base;
}
```

## 枚举（带标签的联合体）

枚举既可表示一组常量，也可作为联合体使用，支持包含不同类型的值。

### 基本定义
```rust
enum Bar {
  RED = 0;
  GREEN = 1;
  BLUE = 2;
}
```

1. **省略值**  
   - 第一个枚举成员默认为 0，其后成员值依次递增。
   ```rust
   enum Foo {
     A;          // 0
     B;          // 1
     C = -10;
     D;          // -9
   }
   ```

2. **值不可重复**  
   - 不同枚举成员的值不能相同。
   ```rust
   enum Foo {
     A = 42;
     B = 42;     // Error: duplicate value
   }

   enum Bar {
     A;          // 0
     B = -1;
     C;          // Error: A and C have the same value 0
   }
   ```

3. **联合体功能（Tagged Union）**  
   - 枚举元素可包含不同类型。
   - 使用时，枚举类型充当联合体，实际数据类型由标签值决定：
   ```rust
   enum Color {
     RED = 0xff << 0o20;
     GREEN = 0xff << 0o10;
     BLUE = 0xff << 0o00;
   }

   struct RGB {
     r: u8;
     g: u8;
     b: u8;
   }

   enum ColorName {
     undefined;              // 0
     color: Color = 0x1;     // 1
     rgb: RGB = 0x2;         // 2
     name: String = 0x3;     // 3
   }
   // 用法示例：
   // if ColorName.tag == 0 : 表示 undefined
   // if ColorName.tag == 1 : 数据类型为 Color
   // if ColorName.tag == 2 : 数据类型为 RGB
   // if ColorName.tag == 3 : 数据类型为 String
   ```

## 接口

接口定义中只支持包含方法声明。接口支持单继承和多继承：
```rust
interface BaseA {
  baseAFunc(): u32;
}

interface BaseB {
  baseBFunc(): u32;
}

interface Derived: BaseA, BaseB {
  derivedFunc(): String;
}
```

通过在接口方法前添加 `functor` 属性将接口声明为函子（即在受支持的语言中，该接口方法将被映射为对括号表达式的重载）。
```rust
interface MyCallback {
  [functor] call(a: u64): u64;
}
```

```cpp
MyCallback cb = ...;
uint64_t ret = cb(42);
```

## 属性

属性定义为键值对，支持附加在多种元素上。

### 基本语法
```rust
[pkgname = "package_func_1", index = 1, has_return_val = FALSE]
function func_1(color: RGB): void;
```

1. **属性可省略值**  
   默认值为 `None`：
   ```rust
   [tuple]
   struct IntPair {
     n: i32;
     m: i32;
   }
   ```

2. **文件级属性**  
   每个文件仅能有一个文件级属性，位于文件末尾：
   ```rust
   [file_info = "测试"]
   ```

3. **属性定义位置**  
   属性需紧邻目标元素上方：
   ```rust
   [tuple]
   struct IntPair {
     [pkgname = "package", baseinfo]
     n: i32;
     m: i32;
   }
   ```

## 其他规则

1. **声明顺序**
   - 函数和类型的声明无先后顺序。
   - 禁止结构体与联合体的递归包含：
     ```rust
     struct Foo {
       bar: Bar;
     }
     struct Bar {
       val: i32;
     } // OK

     struct RecursiveStruct {
       e: RecursiveEnum;
     }
     enum RecursiveEnum {
       s: RecursiveStruct;  // Error: recursive inclusion
     }
     ```

2. **接口递归扩展**  
   接口间不能递归继承：
   ```rust
   interface RecursiveIfaceA: RecursiveIfaceB {}
   interface RecursiveIfaceB: RecursiveIfaceA {}  // Error
   ```
