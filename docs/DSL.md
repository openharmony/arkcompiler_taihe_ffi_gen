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
   ```ts
   // example.types.taihe
   struct Foo {}
   struct Bar {}

   function func1(bar: example1.Foo): void; // OK
   function func2(foo: Foo): void;          // OK
   ```

2. **导入其他包并生成别名**
   使用 `use ... as` 或 `from ... use` 为其他包的名称生成别名。
   ```ts
   // example.test1.taihe
   use example.types as myfoo;
   function func3(foo: myfoo.Foo): void;    // OK

   // example.test2.taihe
   from example.types use Bar, Foo as Foobar;
   function func4(foo: Foobar): void;       // OK
   function func5(foo: Bar): void;          // OK
   ```

3. **包间互相隔离，无从属关系**
   ```ts
   // example.taihe
   from types use Foo;            // Error: package `types` does not exist
   use types as mytypes;          // Error: package `types` does not exist
   from example.types use Foo;    // OK
   use example.types;             // OK
   function func6(foo: Foo): void;           // OK
   function func7(foo: example.types.Foo): void; // OK
   ```

## 内置类型

提供以下基础类型：

- **整型**
  - 无符号：`u8`, `u16`, `u32`, `u64`  注：ArkTS 1.2 不支持无符号类型
  - 有符号：`i8`, `i16`, `i32`, `i64`
- **浮点型**
  - `f32`, `f64`
- **布尔型**
  - `bool`
- **字符串类型**
  - `String`
- **容器类型**
  - `Optional<T>`：可选类型，表示值可能存在或不存在，支持任意类型 `T`。
  - `Array<T>`：定长数组类型，支持任意类型 `T`。
  - `Map<K, V>`：映射类型，支持键值对，其中键类型为 `K`，值类型为 `V`。
  - `Set<T>`：集合类型，支持任意类型 `T`。
  - `Vector<T>`：可动态变长的数组类型，支持任意类型 `T`。
- **函数闭包类型**
  - `(arg1: Type1, arg2: Type2, ...) => ReturnType`：表示函数类型，支持任意数量的参数和一个返回值。

## 函数

支持定义全局函数。

### 函数参数

函数可拥有任意数量的参数，每个参数由参数名和参数类型组成。

### 返回值

函数最多只能有一个返回值。若需返回多个值，可以用结构体表示。

合法与非法声明示例：
```ts
function func(foo: i32): void;                    // OK
function func(foo: String);                       // OK
function func(m: i32, n: i32): (String, String);  // Error: cannot have multiple return values
struct StringPair {
  a: String;
  b: String;
}
function func(m: i32, n: i32): StringPair;        // OK
```

## 枚举

枚举用于定义一组命名的常量，支持整数、浮点数、布尔值和字符串类型。
```ts
enum Foo: i32 {
  A = 0,
  B = 1,
  C = 2,
}

enum Bar: String {
  X = "x",
  Y = "y",
  Z = "z",
}
```

### 省略枚举值

- 对于整数类型的枚举，若未指定值，则从上一个元素的值递增，第一个元素默认为 0。
  ```ts
  enum Foo: i32 {
    A;          // 0
    B;          // 1
    C = -10;
    D;          // -9
  }
  ```
- 对于字符串类型的枚举，若未指定值，默认使用元素名称作为值。
  ```ts
  enum Bar: String {
    X;          // "X"
    Y;          // "Y"
    Z = "z_value";
  }
  ```
- 对于布尔类型和浮点类型的枚举，默认值为 `false` 或 `0.0`。

### 枚举值重复

枚举值可以在不同的枚举元素中重复，但必须确保类型一致。
```ts
enum Foo: i32 {
  A = 0,
  B = 1,
  C = 1,  // 重复值，合法
}
```

## 结构体

结构体是数据成员的组合，其成员类型包括基础类型、枚举类型、接口类型和其他结构体类型：
```ts
interface Base {}
struct Foo {
  a: i32;
  s: String;
  i: Base;
  x: Array<i32>;
}
```

## 标签联合

标签联合用于表示多种可能的数据类型，每个标签对应一种数据类型。多个标签可以对应同一个数据类型。标签联合的定义方式如下：
```ts
union Foo {
  A: i32,
  B: String,
  C: bool,
  D: Bar,
  E: Bar,
}

struct Bar {
  x: i32;
  y: String;
}
```


## 接口

接口定义中只支持包含方法声明。接口支持单继承和多继承：
```ts
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

## 注解

注解用于为代码中的语法元素添加附加属性。
```ts
// 前缀注解（@name）
@attribute_name(value1, value2, ..., key1 = value1, key2 = value2, ...)
function myFunc(color: RGB): void;

// 内联注解（@!name）
interface MyInterface {
  @!attribute_name(value1, value2, ..., key1 = value1, key2 = value2, ...)
  myMethod(param: Type): ReturnType;
}
```

### 无参数时括号可以省略

```ts
@attribute_name()
function myFunc(): void; // OK

@attribute_name
function myFunc(): void; // OK, same as above
```

### 前缀注解和内联注解

- 前缀注解（语法为 `@name`）用于指定给其后面紧跟的语法元素添加属性。
  ```ts
  @class
  interface MyInterface {
    @get("name")
    getName(): String;
    @set("name")
    setName(name: String): void;
  }

  @promise
  function fetchData(url: String): Response;

  @async
  function processData(data: String): void;

  function test(@optional param: Optional<String>);

  union MyUnion {
    @undefined
    undefinedValue;

    @null
    nullValue;

    stringValue: @arraybuffer Array<i8>;
  }
  ```

- 内联注解（语法为 `@!name`）写在某个域内部（如接口、结构体等或包的顶层），用于为其所在的域对应的语法元素添加属性。
  ```ts
  @!namespace("example", namespace = "a.b")  // 全局注解的唯一写法

  interface MyInterface {
    @!class  // 等价于在 interface 前添加 @class
  }
  ```


## 其他规则

### 递归包含与继承

- 函数和类型的声明无先后顺序。
  ```ts
  struct Foo {
    bar: Bar;
  }
  struct Bar {
    val: i32;
  }
  // OK
  ```

- 禁止结构体与结构体、联合体与联合体、结构体与联合体之间的递归包含：
  ```ts
  struct RecursiveStruct {
    e: RecursiveUnion;
  }
  union RecursiveUnion {
    s: RecursiveStruct;
  }
  // Error: recursive inclusion
  ```

- 接口间不能递归扩展：
  ```ts
  interface RecursiveIfaceA: RecursiveIfaceB {}
  interface RecursiveIfaceB: RecursiveIfaceA {}
  // Error
  ```
