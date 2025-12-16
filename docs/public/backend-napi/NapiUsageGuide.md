# Taihe Napi 用户文档

本文档旨在帮助用户了解如何使用 Taihe 生成 Napi 桥接代码。注意，使用工具需要用户对[Taihe IDL 语言规范](../spec/IdlReference.md)，[Taihe C++ 数据结构用法](../backend-cpp/CppUsageGuide.md)有基础的了解。

## 数据类型映射表

Taihe 支持的基本数据类型包括数字、布尔值和[字符串](../backend-cpp/CppUsageGuide.md#61-字符串string)等，以及更复杂的数据结构，如 [Map](../backend-cpp/CppUsageGuide.md#65-映射map)、[Array](../backend-cpp/CppUsageGuide.md#62-数组array)、[Optional](../backend-cpp/CppUsageGuide.md#63-可选类型optional)、[callback](../backend-cpp/CppUsageGuide.md#67-函数闭包callback) 等，各种数据类型在 ArkTS-Dyn、C++、Taihe 之间的具体的映射关系详见下表。

| ArkTS-Dyn                | C++                                | Taihe                    |
| ------------------------ | ---------------------------------- | ------------------------ |
| number                   | int8_t                             | i8                       |
| number                   | int16_t                            | i16                      |
| number                   | int32_t                            | i32                      |
| number                   | int64_t                            | i64                      |
| number                   | uint8_t                            | u8                       |
| number                   | uint16_t                           | u16                      |
| number                   | uint32_t                           | u32                      |
| number                   | uint64_t                           | u64                      |
| number                   | float                              | f32                      |
| number                   | double                             | f64                      |
| boolean                  | bool                               | bool                     |
| string                   | ::taihe::string                    | String                   |
| ?T                       | ::taihe::optional\<T\>             | Optional\<T\>            |
| Map<K, V>                | ::taihe::map\<K, V\>               | Map\<K, V\>              |
| Record<K, V>             | ::taihe::map\<K, V\>               | @record Map\<K, V\>      |
| Array\<T\>               | ::taihe::array\<T\>                | Array\<T\>               |
| bigint                   | ::taihe::array\<u64\>              | @bigint Array\<u64\>     |
| ArrayBuffer              | ::taihe::array\<u8\>               | @arraybuffer Array\<u8\> |
| Uint8Array               | ::taihe::array\<u8\>               | @typedarray Array\<u8\>  |
| Int8Array                | ::taihe::array\<i8\>               | @typedarray Array\<i8\>  |
| Uint16Array              | ::taihe::array\<u16\>              | @typedarray Array\<u16\> |
| Int16Array               | ::taihe::array\<i16\>              | @typedarray Array\<i16\> |
| Uint32Array              | ::taihe::array\<u32\>              | @typedarray Array\<u32\> |
| Int32Array               | ::taihe::array\<i32\>              | @typedarray Array\<i32\> |
| Float32Array             | ::taihe::array\<f32\>              | @typedarray Array\<f32\> |
| Float64Array             | ::taihe::array\<f64\>              | @typedarray Array\<f64\> |
| BigUint64Array           | ::taihe::array\<u64\>              | @typedarray Array\<u64\> |
| BigInt64Array            | ::taihe::array\<i64\>              | @typedarray Array\<i64\> |
| Object                   | uintptr_t                          | Opaque                   |
| (a: T1, b: T2, ...) => R | ::taihe::callback<R(a: T1, b: T2)> | (a: T1, b: T2) => R      |
| null                     | ::taihe::unit                      | @null unit               |
| undefined                | ::taihe::unit                      | @undefined unit          |

表格展示了不同编程语言（ArkTS-Dyn、C++ 和 Taihe）中数据类型的对应关系。其中使用的 T、K 和 V 代表任意类型，可以在类型系统中进行灵活的定义和组合。

注意，ArkTS-Dyn 的 Map 和 Record 在 Taihe 中本质上都是 Map，所以在 C++ 实现时可以参考 Taihe [Map](../backend-cpp/CppUsageGuide.md#65-映射map) 的用法， ArkTS-Dyn 的 Array，bigint，arraybuffer 和 typedarray 在 Taihe 中本质上都是 Array，所以在 C++ 实现时可以参考 Taihe [Array](../backend-cpp/CppUsageGuide.md#62-数组array) 的用法。

# 包

在 Taihe 原生的语言能力中，只有“[包](../spec/IdlReference.md#包)”的概念，包名和 Taihe IDL 文件名一一对应。以 `foo.bar.baz.ohidl` 为例，对应的 C++ 命名空间为 `::foo::bar::baz`，对应的声明文件为 `foo.bar.baz.d.ts`。

在 Taihe 中，使用 `use` 语法来导入外部声明，可以导入的声明类型包括[枚举](#枚举)，[标签联合](#标签联合)，[结构体](#结构体)，[接口](#接口)。Taihe 有两种导入方式：

1. `from ModuleA use DeclFoo;`

2. `use ModuleA;`

其中，ModuleA 为 Taihe 文件名，DeclFoo 为声明。

为了避免重名导致无法分辨由哪个模块导入的情况，可以使用 `as` 语法：

1. `use A as ModuleA;`

2. `from A use B as ModuleA_B;`

## 使用示例

### Taihe 声明

**`people.ohidl`**

```rust
struct student {
    name: String;
    age: i32;
}
function make_student(): student;
```

**`building.ohidl`**

```rust
from people use student;
struct group {
    member: student;
    number: i32;
}
function make_group(): group;
```

### C++ 实现

**File: `people.ohidl 的 C++ 实现`**

```cpp
::taihe::expected<student, ::taihe::error> make_student() {
  return student{"mike", 22};
}
```

**File: `building.ohidl 的 C++ 实现`**

```cpp
::taihe::expected<group, ::taihe::error> make_group() {
  return group{student{"mary", 20}, 23};
}
```

### ArkTS-Dyn 调用

```typescript
import * as lib_people from "people";
import * as lib_building from "building";

let g = lib_building.make_group();
console.log(g.member.age, g.member.name, g.number);
let p = lib_people.make_student();
console.log(p.age, p.name);
```

输出结果如下：

```sh
20 mary 23
22 mike
```

# 命名空间

在 Taihe 中，使用注解 `@!namespace` 可以为生成的 .d.ts 代码添加一个命名空间。

命名空间注解的语法为 `@!namespace(<mudule_name>, <namespace_name>)`, 表示该文件下面的内容为 `<module_name>` 模块下，`<namespace_name>` 命名空间中的内容。该注解作用于 Taihe 文件。

推荐使用 Taihe 文件的命名为 <module_name>.<namespace_name>.ohidl。

特殊用法：

可以使用 `@!namespace(<mudule_name>)`，使得生成的 .d.ts 文件的文件名更改为 `<module_name>.d.ts`。

## 使用示例

### Taihe 声明

**`my_module_a.ohidl`**

```rust
function baz(): void;
```

**`my_module_a.ns1.ohidl`**

```rust
@!namespace("my_module_a", "ns1")
function noo(): void;
```

**`my_module_a.ns1.ns2.ns3.ns4.ns5.ohidl`**

```rust
@!namespace("my_module_a", "ns1.ns2.ns3.ns4.ns5")
function foo(): void;
```

**生成`my_module_a.d.ts`**

```typescript
export function baz(): void;
export namespace ns1 {
  export function noo(): void;
  export namespace ns2 {
    export namespace ns3 {
      export namespace ns4 {
        export namespace ns5 {
          export function foo(): void;
        }
      }
    }
  }
}
```

可以看到 `my_module_a.ohidl`，`my_module_a.ns1.ohidl` 和 `my_module_a.ns1.ns2.ns3.ns4.ns5.ohidl` 的相应内容都生成在 `my_module_a.d.ts` 里

假如只需要一个 <module_name>.<namespace_name>.ohidl 的文件，无需额外写一个空内容的 <module_name>.ohidl

**`my_module_b.functiontest.ohidl`**

```rust
@!namespace("my_module_b", "functiontest")
function bar(): void;
```

**生成`my_module_b.d.ts`**

```typescript
export namespace functiontest {
  export function bar(): void;
}
```

### C++ 实现

**File: `my_module_a.ohidl 的 C++ 实现`**

```cpp
::taihe::expected<void, ::taihe::error> baz() {
  std::cout << "namespace: my_module_a, func: baz" << std::endl;
  return {};
}
```

**File: `my_module_a.ns1.ohidl 的 C++ 实现`**

```cpp
::taihe::expected<void, ::taihe::error> noo() {
  std::cout << "namespace: my_module_a.ns1, func: noo" << std::endl;
  return {};
}
```

**File: `my_module_a.ns1.ns2.ns3.ns4.ns5.ohidl 的 C++ 实现`**

```cpp
::taihe::expected<void, ::taihe::error> foo() {
  std::cout << "namespace: my_module_a.ns1.ns2.ns3.ns4.ns5, func: noo" << std::endl;
  return {};
}
```

**File: `my_module_b.functiontest.ohidl 的 C++ 实现`**

```cpp
::taihe::expected<void, ::taihe::error> bar() {
  std::cout << "namespace: my_module_b.functiontest, func: bar" << std::endl;
  return {};
}
```

### ArkTS-Dyn 调用

```typescript
import * as lib_a from "my_module_a";
import * as lib_b from "my_module_b";

lib_a.baz();
lib_a.ns1.noo();
lib_a.ns1.ns2.ns3.ns4.ns5.foo();
lib_b.functiontest.bar();
```

输出结果如下：

```sh
namespace: my_module_a, func: baz
namespace: my_module_a.ns1, func: noo
namespace: my_module_a.ns1.ns2.ns3.ns4.ns5, func: noo
namespace: my_module_b.functiontest, func: bar
```

# 全局函数

下面的代码将展示如何书写 Taihe 文件，生成一个全局函数的 Napi 桥接代码及对应的 .d.ts 声明。Taihe 中的[全局函数](../spec/IdlReference.md#函数)参数和返回值可以是任意类型，注意，在使用 Taihe 工具进行 Napi 桥接代码生成时不支持以 `callback` 类型做为函数返回值类型。

## 使用示例

### Taihe 声明

**`.ohidl`**

```rust
function add(a: i32, b: i32): i32;
```

**生成`.d.ts`**

```typescript
export function add(a: number, b: number): number;
```

### C++ 实现

除了书写 Taihe 文件外，还需要[在 C++ 侧实现函数](../backend-cpp/CppUsageGuide.md#71-导出函数接口发布方)

```cpp
::taihe::expected<int32_t, ::taihe::error> add(int32_t a, int32_t b) {
  return a + b;
}
TH_EXPORT_CPP_API_add(add);
```

### ArkTS-Dyn 调用

```typescript
let add_show = add(2, 3);
console.log("function add:", add_show);
```

输出结果如下：

```sh
function add: 5
```

## 函数调用链

以示例函数为例，当 ArkTS-Dyn 侧调用函数 add 时，它会经历如下步骤：

1. 进入生成代码中的注册函数，找到 `add` 对应的函数为 `package_name_add_NAPI0`。

   **register**

   ```cpp
   napi_value Init(napi_env env, napi_value exports) {
    ...
    napi_property_descriptor desc[] = {
        {"add", nullptr, package_name_add_NAPI0, nullptr, nullptr, nullptr, napi_default, nullptr},
    };
    ...
   }
   ```

2. 进入 `.napi.cpp` 文件中 `package_name_add_NAPI0` 函数，它会先解析参数，将 ArkTS-Dyn 对象转换为 Taihe 对象，然后调用 C++ 实现函数，再将返回值由 Taihe 对象转换为 ArkTS-Dyn 对象。

  **.napi.cpp**

  ```cpp
  static napi_value package_name_add_NAPI0(napi_env env, [[maybe_unused]] napi_callback_info info) {
    // 参数解析
    size_t argc = 2;
    napi_value args[2] = {nullptr};
    napi_get_cb_info(env, info, &argc, args , nullptr, nullptr);
    // 参数类型转换
    int32_t value0_tmp;
    napi_get_value_int32(env, args[0], &value0_tmp);
    int32_t value0 = value0_tmp;
    int32_t value1_tmp;
    napi_get_value_int32(env, args[1], &value1_tmp);
    // 调用 C++ 实现
    int32_t value1 = value1_tmp;
    int32_t value = package_name::add(value0, value1);
    // 返回值解析
    napi_value result = nullptr;
    napi_create_int32(env, value, &result);
    // 向上层返回函数调用结果
    return result;
  }
  ```

3. 接下来，`package_name_add_NAPI0` 函数会调用 `package_name::add` 函数，这个函数的调用会被自动转发到 C++ 实现文件中，通过 TH_EXPORT_CPP_API_add 这个宏所导出的具体实现。

   **.impl.cpp**

   ```cpp
   // C++ 实现
   ::taihe::expected<int32_t, ::taihe::error> add(int32_t a, int32_t b) {
     return a + b;
   }
   TH_EXPORT_CPP_API_add(add);
   ```

4. `package_name::add` 函数执行完毕后，将返回第 3 步所示的函数，将获取到的返回值转换为 ArkTS-Dyn 类型，返回给 ArkTS-Dyn 侧函数。

# 枚举

进行枚举类型相关开发时，可以使用 enum，使用常量表示有限的状态。进行常量相关开发时，可以在 enum 上使用 @const 注解。

## 使用示例

### Taihe 声明

**`.ohidl`**

```rust
enum Color: String {
    RED = "Red",
    GREEN = "Green",
    BLUE = "Blue",
}
@const
enum FlagsF32: i32 {
    FLAG_F32_A = 1,
    FLAG_F32_B = 1 + 2,
}
function nextEnum(color: Color): Color;
```

**生成`.d.ts`**

```typescript
export enum Color {
  RED = "Red",
  GREEN = "Green",
  BLUE = "Blue",
}
export const FLAG_F32_A = 1;
export const FLAG_F32_B = 3;
export function nextEnum(color: Color): Color;
```

### C++ 实现

Taihe 中 enum 类型的 C++ 使用方法可参考[枚举类](../backend-cpp/CppUsageGuide.md#2-枚举类)

```cpp
static constexpr std::size_t COLOR_COUNT = 3;
::taihe::expected<Color, ::taihe::error> nextEnum(Color color) {
  return (Color::key_t)(((int)color.get_key() + 1) % COLOR_COUNT);
}
```

### ArkTS-Dyn 调用

```typescript
let color = Color.GREEN;
let nextColor = nextEnum(color);
console.log("nextColor:", nextColor);
console.log("const value:", FLAG_F32_A, FLAG_F32_B);
```

输出结果如下：

```sh
nextColor: Blue
const value: 1 3
```

# 标签联合

需要在同一内存位置存放不同类型的数据时，可以使用 [union](../spec/IdlReference.md#标签联合)。注意，在使用 Taihe 工具进行 Napi 桥接代码生成时，只支持 union 联合基础类型、String、Array、Map、undefined、null 和 Object，当存在 Object 类型时，必须设为 union 的最后一个元素，当存在 undefined 类型或 null 类型时需要定义在其他类型之前。

## 使用示例

### Taihe 声明

**`.ohidl`**

```rust
union union_primitive {
  uValue: @undefined unit;
  nValue: @null unit;
  sValue: String;
  numberValue: f64;
  bValue: bool;
  aValue: Array<i32>;
  mValue: Map<i32, String>;
}

function printUnion(data: union_primitive): String;
function makeUnion(kind: String): union_primitive;
```

**生成`.d.ts`**

```typescript
export function printUnion(data: union_primitive): string;
export function makeUnion(kind: string): union_primitive;
export type union_primitive =
  | undefined
  | null
  | string
  | number
  | boolean
  | Array<number>
  | Map<number, string>;
```

### C++ 实现

Taihe 中 union 类型的 C++ 使用方法可参考[联合体](../backend-cpp/CppUsageGuide.md#4-联合体)

```cpp
::taihe::expected<::taihe::string, ::taihe::error> printUnion(union_primitive const &data) {
  switch (data.get_tag()) {
  case union_primitive::tag_t::sValue:
    std::cout << "s: " << data.get_sValue_ref() << std::endl;
    return "s";
  case union_primitive::tag_t::numberValue:
    std::cout << "number: " << (int)data.get_numberValue_ref() << std::endl;
    return "number";
  case union_primitive::tag_t::bValue:
    std::cout << "bool: " << data.get_bValue_ref() << std::endl;
    return "bool";
  case union_primitive::tag_t::aValue:
    std::cout << "array: " << data.get_aValue_ref()[0] << std::endl;
    return "array";
  case union_primitive::tag_t::mValue:
    std::cout << "map: " << std::endl;
    for (auto const &[key, val] : data.get_mValue_ref()) {
      std::cout << "C++ Map: key: " << key << " value: " << val << std::endl;
    }
    return "map";
  case union_primitive::tag_t::uValue:
    return "undefined";
  case union_primitive::tag_t::nValue:
    return "null";
  }
}

::taihe::expected<union_primitive, ::taihe::error> makeUnion(::taihe::string_view kind) {
  ::taihe::string s_value = "string";
  constexpr double f64_value = 1.12345;
  constexpr bool bool_value = false;
  ::taihe::array<int32_t> array_value = ::taihe::array<int32_t>{1, 2, 3};
  ::taihe::map<int32_t, ::taihe::string> map_value;
  map_value.emplace(1, "a");
  map_value.emplace(2, "b");

  if (kind == "s") {
    return union_primitive::make_sValue(s_value);
  }
  if (kind == "number") {
    return union_primitive::make_numberValue(f64_value);
  }
  if (kind == "bool") {
    return union_primitive::make_bValue(bool_value);
  }
  if (kind == "array") {
    return union_primitive::make_aValue(array_value);
  }
  if (kind == "map") {
    return union_primitive::make_mValue(map_value);
  }
  if (kind == "undefined") {
    return union_primitive::make_uValue();
  }
  if (kind == "null") {
    return union_primitive::make_nValue();
  }
  return union_primitive::make_uValue();
}
```

### ArkTS-Dyn 调用

```typescript
console.log(printUnion(1));
console.log(makeUnion("s"));
```

输出结果如下：

```sh
number: 1
Test: number
Test: string
```

# 结构体

进行纯数据类型的接口相关开发时，可以使用 [struct](../spec/IdlReference.md#结构体)。struct 是数据成员的组合，其成员可以是任意 Taihe 中的数据类型，包括[基础类型](#数据类型映射表)、[枚举类型](#枚举)、[接口类型](#接口)、[标签联合](#标签联合)和其他[结构体类型](#结构体)等。

## 使用示例

### Taihe 声明

**`.ohidl`**

```rust
struct RGB {
    r: i32;
    g: i32;
    b: i32;
}
function from_rgb(rgb: RGB): i32;
```

**生成`.d.ts`**

```typescript
export interface RGB {
  r: number;
  g: number;
  b: number;
}
export function from_rgb(rgb: RGB): number;
```

如果需要设置 struct 中某个属性为只读属性，可以使用 @readonly 注解。
**`.ohidl`**

```rust
struct Student {
    @readonly name: String;
    age: i32;
}
function process_student(a: Student): Student;
```

**生成`.d.ts`**

```typescript
export interface Student {
  readonly name: string;
  age: number;
}
export function process_student(a: Student): Student;
```

如果需要生成数据类型为 class 而不是 interface 可以使用 @class 注解。可以使用 @static 注解标记全局函数为某个 class 的静态方法，可以使用 @ctor 注解标记全局函数为某个 class 的构造函数。

注意，使用 @class 时通常需要提供构造函数，除非确认无需在 ets 层使用 new 实例化。

**`.ohidl`**

```rust
@class
struct Teacher {
    @readonly name: String;
    age: i32;
}

@static("Teacher")
function give_lessons(): String;

@ctor("Teacher")
function create_teacher(): Teacher;
function process_teacher(a: Teacher): Teacher;
```

**生成`.d.ts`**

```typescript
export class Teacher {
  readonly name: string;
  age: number;
  constructor();
  static give_lessons(): string;
}
export function process_teacher(a: Teacher): Teacher;
```

如果存在继承关系，可以使用 @extends 注解。@extends item_name: item_type，此处的 item_name 用于 C++ 侧，在 ArkTS-Dyn 侧无作用；item_type 为用户实际希望继承的 struct 声明。注意，Taihe 只支持 struct 继承 struct，@class struct 继承 struct。
**`.ohidl`**

```rust
struct F {
    f: i32;
}

struct G {
    @extends f: F;
    g: i32;
}

@class
struct H {
    @extends g: G;
    h: i32;
}

@ctor("H")
function create_h(f: i32, g: i32, h: i32): H;

function process_g(a: G): G;
function process_h(a: H): H;
```

**生成`.d.ts`**

```typescript
export interface F {
  f: number;
}
export interface G extends F {
  g: number;
}
export class H implements G {
  f: number;
  g: number;
  h: number;
  constructor(f: number, g: number, h: number);
}
export function process_g(a: G): G;
export function process_h(a: H): H;
```

### C++ 实现

Taihe 中 struct 类型的 C++ 使用方法可参考[结构体](../backend-cpp/CppUsageGuide.md#3-结构体)

```cpp
::taihe::expected<int32_t, ::taihe::error> from_rgb(RGB const &rgb) {
  return rgb.r + rgb.g + rgb.b;
}
::taihe::expected<Student, ::taihe::error> process_student(Student const &a) {
  return Student{a.name + " student", a.age + 10};
}
::taihe::expected<Teacher, ::taihe::error> process_teacher(Teacher const &a) {
  return Teacher{a.name + " teacher", a.age + 15};
}
::taihe::expected<G, ::taihe::error> process_g(G const& a) {
  return {{a.f.f + 1}, a.g + 2};
}
::taihe::expected<H, ::taihe::error> process_h(H const& a) {
  return H{{{a.g.f.f + 1}, a.g.g + 2}, a.h +3};
}
::taihe::expected<H, ::taihe::error> create_h(int32_t f, int32_t g, int32_t h) {
  return H{{{f}, g}, h};
}
::taihe::expected<Teacher, ::taihe::error> create_teacher() {
  return Teacher{"Rose", 25};
}
::taihe::expected<::taihe::string, ::taihe::error> give_lessons() {
  return "math";
}
```

### ArkTS-Dyn 调用

```typescript
// 初始化 interface 类型变量
let rgb: RGB = { r: 1, g: 2, b: 3 };
let my_rgb_i32 = from_rgb(rgb);
console.log("from ts RGB to i32:", my_rgb_i32);

let student: Student = { name: "Jack", age: 10 };
let pro_student = process_student(student);
console.log("process student:", pro_student.name, pro_student.age);

// Test struct class constructor
let cre_teacher = new Teacher();
console.log("create teacher: ", cre_teacher.name, cre_teacher.age);
let pro_teacher = process_teacher(cre_teacher);
console.log("process teacher: ", pro_teacher.name, pro_teacher.age);

// Test struct class static function
let lesson = Teacher.give_lessons();
console.log("teacher static function give lessons:", lesson);

let g = { f: 0, g: 0 };
let new_g = process_g(g);
console.log("process g:", new_g.f, new_g.g);

let h = new H(0, 0, 0);
let new_h = process_h(h);
console.log("process h:", new_h.f, new_h.g, new_h.h);
```

输出结果如下：

```sh
from ts RGB to i32: 6
process student: Jack student 20
create teacher:  Rose 25
process teacher:  Rose teacher 40
teacher static function give lessons: math
process g: 1 2
process h: 1 2 3
```

# 接口

进行纯方法类型的接口相关开发时，可以使用 [interface](../backend-cpp/CppUsageGuide.md#5-接口)。

## 使用示例

### Taihe 声明

**`.ohidl`**

```rust
interface IBase {
    getId(): String;
    setId(s: String): void;
}
function makeIBase(id: String): IBase;
function copyIBase(a: IBase, b: IBase): void;
```

**生成`.d.ts`**

```typescript
export interface IBase {
  getId(): string;
  setId(s: string);
}
export function makeIBase(id: string): IBase;
export function copyIBase(a: IBase, b: IBase): void;
```

当接口内既包含方法，又包含数据时，可以通过 @get 或 @set 注解来说明将特定方法声明为数据的 getter 或 setter。

**`.ohidl`**

```rust
interface IColor {
    @get getId(): String;
    @set setId(s: String): void;
    calculate(a: i32, b: i32): i32;
}

function makeIColor(id: String): IColor;
```

**生成`.d.ts`**

```typescript
export interface IColor {
  get Id(): string;
  set Id(s: string);
  calculate(a: number, b: number): number;
}
export function makeIColor(id: string): IColor;
```

如果需要生成数据类型为 class 而不是 interface 可以使用 @class 注解。可以使用 @static 注解标记全局函数为某个 class 的静态方法，可以使用 @ctor 注解标记全局函数为某个 class 的构造方法。

**`.ohidl`**

```rust
@class
interface CTest{
    add(a: i32, b: i32): f32;
}

@ctor("CTest")
function createCTest(id: i32): CTest;

@static("CTest")
function multiply(a: i32, b: i32): i32;

function changeCTest(a: CTest): CTest;
```

**生成`.d.ts`**

```typescript
export class CTest {
  constructor(id: number);
  static multiply(a: number, b: number): number;
  add(a: number, b: number): number;
}
export function changeCTest(a: CTest): CTest;
```

Taihe IDL 语法支持 [interface](../spec/IdlReference.md#接口) 单继承和多继承，interface A: B, C {} 表示 interface A 继承了 interface B 和 interface C。注意，Taihe 只支持 interface 继承 interface，@class interface 继承 interface。

**`.ohidl`**

```rust
interface IShape: IBase {
    calculateArea(): f64;
}

function makeIShape(id: String, a: f64, b: f64): IShape;

@class
interface IDerived: IShape {
    call(): void;
}

@ctor("IDerived")
function createIDerived(): IDerived;
```

**生成`.d.ts`**

```typescript
export interface IShape extends IBase {
  calculateArea(): number;
}
export class IDerived implements IShape {
  constructor();
  call();
  calculateArea(): number;
  getId(): string;
  setId(s: string);
}
export function makeIShape(id: string, a: number, b: number): IShape;
```

### C++ 实现

Taihe 中 interface 类型的 C++ 使用方法可参考[接口](../backend-cpp/CppUsageGuide.md#5-接口)。

```cpp
class Base {
protected:
  ::taihe::string id;

public:
  Base(::taihe::string_view id) : id(id) {
    std::cout << "new base " << this << std::endl;
  }

  ~Base() {
    std::cout << "del base " << this << std::endl;
  }

  ::taihe::expected<::taihe::string, ::taihe::error> getId() {
    return id;
  }

  ::taihe::expected<void, ::taihe::error> setId(::taihe::string_view s) {
    id = s;
    return {};
  }
};

class Shape {
protected:
  ::taihe::string id;
  float a;
  float b;

public:
  Shape(::taihe::string_view id, float a, float b) : id(id), a(a), b(b) {
    std::cout << "new shape " << this << std::endl;
  }

  ~Shape() {
    std::cout << "del shape " << this << std::endl;
  }

  ::taihe::expected<::taihe::string, ::taihe::error> getId() {
    return id;
  }

  ::taihe::expected<void, ::taihe::error> setId(::taihe::string_view s) {
    id = s;
    return {};
  }

  ::taihe::expected<float, ::taihe::error> calculateArea() {
    return a * b;
  }
};

class CTestImpl {
  int32_t x;

public:
  CTestImpl(int32_t x) : x(x) {
    std::cout << "new ctest " << this->x << std::endl;
  }

  ~CTestImpl() {
    std::cout << "del ctest " << this << std::endl;
  }

  ::taihe::expected<float, ::taihe::error> add(int32_t a, int32_t b) {
    return a + b + this->x;
  }
};

class Color {
protected:
  ::taihe::string id;

public:
  Color(::taihe::string_view id) : id(id) {
    std::cout << "new Color " << this << std::endl;
  }

  ~Color() {
    std::cout << "del Color " << this << std::endl;
  }

  ::taihe::expected<::taihe::string, ::taihe::error> getId() {
    return id;
  }

  ::taihe::expected<void, ::taihe::error> setId(::taihe::string_view s) {
    id = s;
    return {};
  }

  ::taihe::expected<int32_t, ::taihe::error> calculate(int32_t a, int32_t b) {
    return a * b;
  }
};

class Derived {
protected:
  ::taihe::string id = "d";
  float a = 1;
  float b = 2;

public:
  ::taihe::expected<void, ::taihe::error> call() {
    std::cout << "derived call!" << std::endl;
    return {};
  }

  ::taihe::expected<double, ::taihe::error> calculateArea() {
    return a * b;
  }

  ::taihe::expected<::taihe::string, ::taihe::error> getId() {
    return id;
  }

  ::taihe::expected<void, ::taihe::error> setId(::taihe::string_view s) {
    this->id = s;
    return {};
  }
};

::taihe::expected<IBase, ::taihe::error> makeIBase(::taihe::string_view id) {
  return ::taihe::make_holder<Base, IBase>(id);
}

::taihe::expected<void, ::taihe::error> copyIBase(weak::IBase a, weak::IBase b) {
  a->setId(b->getId());
  return {};
}

::taihe::expected<IShape, ::taihe::error> makeIShape(::taihe::string_view id, double a, double b) {
  return ::taihe::make_holder<Shape, IShape>(id, a, b);
}

::taihe::expected<CTest, ::taihe::error> createCTest(int32_t id) {
  return taihe::make_holder<CTestImpl, CTest>(id);
}

::taihe::expected<CTest, ::taihe::error> changeCTest(weak::CTest a) {
  int32_t x = a->add(3, 4);
  return taihe::make_holder<CTestImpl, CTest>(x);
}

::taihe::expected<int32_t, ::taihe::error> multiply(int32_t a, int32_t b) {
  return a * b;
}

::taihe::expected<IColor, ::taihe::error> makeIColor(::taihe::string_view id) {
  return taihe::make_holder<Color, IColor>(id);
}

::taihe::expected<IDerived, ::taihe::error> createIDerived() {
  return taihe::make_holder<Derived, IDerived>();
}
```

### ArkTS-Dyn 调用

```typescript
class BaseImpl implements IBase {
  id: string;
  constructor(id: string) {
    this.id = id;
  }
  getId(): string {
    return this.id;
  }
  setId(id: string): void {
    this.id = id;
    return;
  }
}

// 创建父类接口
let ibase_1 = makeIBase("abc");
console.log("ibase_1 getId: ", ibase_1.getId());

// 父类接口调用父类接口声明函数
ibase_1.setId("xyz");
console.log("ibase_1 setId: ", ibase_1.getId());

let ibase_2 = makeIBase("test");
copyIBase(ibase_1, ibase_2);
console.log("copyIBase: ", ibase_1.getId(), ibase_2.getId());

// 创建子类接口
let ishape_1 = makeIShape("shape", 3.14, 2.5);

// 子类接口调用子类接口声明函数
console.log("makeIShape: ", ishape_1.calculateArea());
// 子类接口调用父类接口声明函数
console.log("interface extends: ", ishape_1.getId());

ishape_1.setId("aaaaa");
console.log("interface extends set: ", ishape_1.getId());

let a: BaseImpl = new BaseImpl("A");
let b: BaseImpl = new BaseImpl("B");
copyIBase(b, a);
console.log("impl interface: ", a.getId(), b.getId());

// 子类接口实例赋值给父类接口参数
copyIBase(ibase_1, ishape_1);
console.log("interface extends: ", ibase_1.getId(), ishape_1.getId());

// 创建 interface class
let ctest = new CTest(100);
console.log("CTets: ", ctest.add(1, 2));

// 调用 interface class 声明方法
let new_ctest = changeCTest(ctest);
console.log("change CTets: ", new_ctest.add(5, 6));

// 调用 interface class 声明的静态方法
let value3 = CTest.multiply(7, 8);
console.log("static function: ", value3);

let color = makeIColor("my color");
console.log("get attr: ", color.Id);
color.Id = "new my color";
console.log("set attr: ", color.Id);
console.log("color method: ", color.calculate(2, 3));

let d = new IDerived();
d.call();
// 子类接口调用父类声明方法
console.log(d.getId());
```

输出结果如下：

```sh
new base 0x1d579b60
ibase_1 getId:  abc
ibase_1 setId:  xyz
new base 0x1d53cc00
copyIBase:  test test
new shape 0x1d55fbb0
makeIShape:  7.850000381469727
interface extends:  shape
interface extends set:  aaaaa
impl interface:  A A
interface extends:  aaaaa aaaaa
new ctest 100
CTets:  103
new ctest 107
change CTets:  118
static function:  56
new Color 0x1d53c680
get attr:  my color
set attr:  new my color
color method:  6
derived call!
d
del Color 0x1d53c680
del ctest 0x1d53b290
del ctest 0x1d53a880
del shape 0x1d55fbb0
del base 0x1d53cc00
del base 0x1d579b60
```

# 异步

使用注解 `@async` 将声明的函数或方法转换为Async版，使用注解 `@promise` 将声明的函数或方法转换为Promise版。

## 使用示例

### Taihe 声明

**`.ohidl`**

```rust
function addSync(a: i32, b: i32): i32;
@promise function addRetPromise(a: i32, b: i32): i32;
@async function addWithAsync(a: i32, b: i32): i32;

@class
interface IBase {
    @promise makeRetPromise();
    @async makeWithAsync();
    makeSync();
}
@ctor("IBase")
function createIBase(): IBase;
```

**生成`.d.ts`**

```typescript
type AsyncCallback<T> = (error: Error | null, result: T | undefined) => void;
export function addSync(a: number, b: number): number;
export function addRetPromise(a: number, b: number): Promise<number>;
export function addWithAsync(a: number, b: number, callback: AsyncCallback<number>): void;

export class IBase {
    constructor();
    makeRetPromise(): Promise<void>;
    makeWithAsync(callback: AsyncCallback<void>): void;
    makeSync(): void;
}
```

### C++ 实现

在 C++ 侧函数正常书写同步实现即可，异步操作将在自动代码生成的 NAPI 层代码中完成，当函数中希望抛出异常时，可以构造出一个 `taihe::expected` 对象作为返回值，其中包含可能希望返回的错误信息与错误码等，具体使用方式请参考[异常和错误](../backend-cpp/CppUsageGuide.md)。

```cpp
::taihe::expected<int32_t, ::taihe::error> addSync(int32_t a, int32_t b) {
  if (a == 0) {
    std::cout << "throw error in addSync impl " << std::endl;
    return ::taihe::expected<int32_t, ::taihe::error>(::taihe::unexpect,
                                                      "some error happen");
  } else {
    std::cout << "add impl " << a + b << std::endl;
    return a + b;
  }
}

::taihe::expected<int32_t, ::taihe::error> addRetPromise(int32_t a, int32_t b) {
  std::this_thread::sleep_for(std::chrono::milliseconds(100));

  if (a == 0) {
    std::cout << "ERROR in addRetPromise" << std::endl;
    return ::taihe::expected<int32_t, ::taihe::error>(::taihe::unexpect,
                                                      "some error happen");
  } else {
    std::cout << "SUCCESS in addRetPromise: " << a + b << std::endl;
    return a + b;
  }
}

::taihe::expected<int32_t, ::taihe::error> addWithAsync(int32_t a, int32_t b) {
  std::this_thread::sleep_for(std::chrono::milliseconds(50));

  if (a == 0) {
    std::cout << "ERROR in addWithAsync" << std::endl;
    return ::taihe::expected<int32_t, ::taihe::error>(::taihe::unexpect,
                                                      "some error happen");
  } else {
    std::cout << "SUCCESS in addWithAsync: " << a + b << std::endl;
    return a + b;
  }
}

class IBaseImpl {
public:
  ::taihe::expected<void, ::taihe::error> makeSync() {
    std::cout << "makeSync" << std::endl;
    return {};
  }

  ::taihe::expected<void, ::taihe::error> makeRetPromise() {
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    std::cout << "makeRetPromise" << std::endl;
    return {};
  }

  ::taihe::expected<void, ::taihe::error> makeWithAsync() {
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    std::cout << "makeWithAsync" << std::endl;
    return {};
  }
};
::taihe::expected<::async_test::IBase, ::taihe::error> createIBase() {
  return taihe::make_holder<IBaseImpl, ::async_test::IBase>();
}

TH_EXPORT_CPP_API_addSync(addSync);
TH_EXPORT_CPP_API_addRetPromise(addRetPromise);
TH_EXPORT_CPP_API_addWithAsync(addWithAsync);
TH_EXPORT_CPP_API_createIBase(createIBase);
```

### ArkTS-Dyn 调用

```typescript
console.log("before call function addRetPromise success");
let p1 = lib.addRetPromise(1, 2);
p1.then((res) => {
    console.log("success in addRetPromise", res);
})
.catch((ret) => {
    console.log("failed in addRetPromise", ret);
});
console.log("after call function addRetPromise success");

console.log("before call function addRetPromise failed");
let p2 = lib.addRetPromise(0, 2);
p2.then((res) => {
    console.log("success in addRetPromise", res);
})
.catch((ret) => {
    console.log("failed in addRetPromise", ret.message);
});
console.log("after call function addRetPromise failed");

console.log("before call function addWithAsync success");
lib.addWithAsync(1, 2, (error, result) => {
    if (error !== null) {
        console.log("failed in addWithAsync", error.message);
    } else {
        console.log("success in addWithAsync", result!);
    }
})
console.log("after call function addWithAsync success");

console.log("before call function addWithAsync failed");
lib.addWithAsync(0, 2, (error: Error | null, result?: number) => {
    if (error !== null) {
        console.log("failed in addWithAsync", error.message);
    } else {
        console.log("success in addWithAsync", result!);
    }
})
console.log("after call function addWithAsync failed");

let mybase = new lib.IBase();
mybase.makeSync();
mybase.makeRetPromise();
mybase.makeWithAsync((error: Error | null) => {
    if (error !== null) {
        console.log("failed in make", error.message);
    } else {
        console.log("success in make");
    }
});
```

输出结果如下：

```sh
before call function addRetPromise success
after call function addRetPromise success
before call function addRetPromise failed
after call function addRetPromise failed
before call function addWithAsync success
after call function addWithAsync success
before call function addWithAsync failed
after call function addWithAsync failed
makeSync
finish main
SUCCESS in addWithAsync: 3
ERROR in addWithAsync
success in addWithAsync 3
failed in addWithAsync some error happen
SUCCESS in addRetPromise: 3
ERROR in addRetPromise
success in addRetPromise 3
failed in addRetPromise some error happen
makeWithAsync
success in make
makeRetPromise
```


# 逃逸通道 - Napi 协同开发

Taihe 支持引入 Napi 代码，从而在 C++ 侧访问 ArkTS-Dyn 对象，可以使用 Opaque 类型，对应 Napi 类型为 napi_value，C++ 类型为指针。可以使用 @dts_type 注解指定 Opaque 在 .d.ts 文件中的类型， @dts_type("<type_name>") Opaque, <type_name> 为 .d.ts 中的类型名。

可以引用 taihe/napi_runtime.hpp 头文件，其中提供 get_env() 函数返回 napi_env 指针，set_error() 函数抛出错误，set_type_error() 函数抛出类型错误，set_range_error() 函数抛出范围错误，has_error() 函数判断是否存在错误。

## 使用示例

### Taihe 声明

```rust
function is_string(s: Opaque): bool;
function get_object(): @dts_type("string") Opaque;
function get_objects(): Array<@dts_type("any") Opaque>;
union Union {
  sValue: String;
  oValue: Opaque;
}
struct Person{
  name: String;
}
function is_opaque(s: Union): bool;
```

**生成`.d.ts`**

```typescript
export function is_string(s: Object): boolean;
export function get_object(): string;
export function get_objects(): Array<any>;
export function is_opaque(s: Union): boolean;
export type Union = string | Object;
export interface Person {
  name: string;
}
```

### C++ 实现

```cpp
::taihe::expected<bool, ::taihe::error> is_string(uintptr_t s) {
  napi_env env = ::taihe::get_env();
  napi_valuetype value_ty;
  napi_typeof(env, (napi_value)s, &value_ty);
  if (value_ty == napi_string) {
    return true;
  } else {
    return false;
  }
}

::taihe::expected<uintptr_t, ::taihe::error> get_object() {
  napi_env env = ::taihe::get_env();
  napi_value napi_arr_0 = nullptr;
  ::taihe::string cpp_arr_0 = "OnlyObject";
  napi_create_string_utf8(env, cpp_arr_0.c_str(), cpp_arr_0.size(),
                          &napi_arr_0);
  return (uintptr_t)napi_arr_0;
}

::taihe::expected<::taihe::array<uintptr_t>, ::taihe::error> get_objects() {
  napi_env env = ::taihe::get_env();
  napi_value napi_arr_0 = nullptr;
  ::taihe::string cpp_arr_0 = "FirstOne";
  napi_create_string_utf8(env, cpp_arr_0.c_str(), cpp_arr_0.size(),
                          &napi_arr_0);
  napi_value napi_arr_1 = nullptr;
  napi_get_undefined(env, &napi_arr_1);
  return ::taihe::array<uintptr_t>(
      {(uintptr_t)napi_arr_0, (uintptr_t)napi_arr_1});
}

::taihe::expected<bool, ::taihe::error> is_opaque(Union const &s) {
  if (s.get_tag() == Union::tag_t::oValue) {
    return true;
  }
  return false;
}
```

### ArkTS-Dyn 调用

```typescript
console.log("test opaque param", is_string("test"));
console.log("test opaque param", is_string(2));

console.log("test opaque return value", get_object());

let arr = get_objects();
console.log("test opaque return array value", arr[0], arr[1]);

let p: Person = { name: "Mary" };
console.log("test opaque param union", is_opaque(p));
console.log("test opaque param union", is_opaque("1"));
```

输出结果如下：

```sh
test opaque param true
test opaque param false
test opaque return value OnlyObject
test opaque return array value FirstOne undefined
test opaque param union true
test opaque param union false
```

# 逃逸通道 - ArkTS-Dyn 协同开发

Taihe 支持引入 ArkTS-Dyn 代码，从而在 ArkTs 层添加代码。

## 使用示例

### Taihe 声明

默认情况下，Taihe 会生成 Napi 桥接文件和 .d.ts 文件，此时，可以使用注解 @!dts_inject_into_module 将一段 ArkTS-Dyn 代码注入到当前 Taihe 文件所对应的 .d.ts 文件的 namespace 中；可以使用注解 @!dts_inject 将一段 ArkTS-Dyn 代码注入到当前 Taihe 文件所对应的 .d.ts 文件的 namespace 所在的 module 头部。

**`my_module_b.functiontest.ohidl`**

```rust
@!namespace("my_module_b", "functiontest")

@!dts_inject_into_module("export const rate = 0.618;")
@!dts_inject("""export function concat(a: string | number): string | number;""")
function concat_str(a: String): String;
function concat_i32(a: i32): i32;
```

**生成`my_module_b.d.ts`**

```typescript
export const rate = 0.618;
export namespace functiontest {
  export function concat(a: string | number): string | number;
  export function concat_str(a: string): string;
  export function concat_i32(a: number): number;
}
```

特殊情况下（即使用 @!lib 注解时），Taihe 会额外生成与 .d.ts 文件同名的 .ts 文件存储在 //generated/proxy 目录下，做为 proxy 层代理 C++ 层已完成的实现，同时支持用户通过 inject 在 ts 层注入实现。

注意，如果需要让当前 Taihe 文件对应的 module 生成 .ts 文件，或在当前 Taihe 文件中使用 ts inject 相关功能，必须提供 @!lib 注解。其语法为 @!lib("{so_file}")，使用注解时需指定 so 文件，作用是为生成的 .ts 文件提供寻找 C++ 层的实现。

此时，可以使用注解 @!ts_inject_into_module 将一段 ArkTS-Dyn 代码注入到当前 Taihe 文件所对应的 .ts 文件的 namespace 中；可以使用注解 @!ts_inject 将一段 ArkTS-Dyn 代码注入到当前 Taihe 文件所对应的 .ts 文件的 namespace 所在的 module 头部；可以使用注解 @!ts_inject_into_interface 将一段 ArkTS-Dyn 代码注入到当前 interface 中；可以使用注解 @!ts_inject_into_class 将一段 ArkTS-Dyn 代码注入到当前 interface 对应的 class 中。

注意，@!ts_inject_into_interface 注解应用于 struct 和 interface，@!ts_inject_into_class 注解可以应用于添加了 @class 注解的 struct 和 interface。

**`my_module_a.ohidl`**

```rust
@!lib("my_module_a")
function concat_str(a: String): String;
function concat_i32(a: i32): i32;

// global function overload example
@!ts_inject("""export function concat(a: string | number): string | number {
    if (typeof a === "string") {
        return concat_str(a);
    } else {
        return concat_i32(a);
    }
}""")
```

**`my_module_a.ns1.ohidl`**

```rust
@!lib("my_module_a")
@!namespace("my_module_a", "ns1")

interface IBase {
@!ts_inject_into_interface("add(a: number, b: number): number;")
    getId(): String;
    setId(s: String): void;
}

@class
interface CTest{
@!ts_inject_into_class("""mul(a: number, b: number): number {
    return a * b;
}
""")
    add(a: i32, b: i32): f32;
}

@ctor("CTest")
function createCTest(id: i32): CTest;

@static("CTest")
function multiply(a: i32, b: i32): i32;
```

**`my_module_a.ns1.ns2.ns3.ns4.ns5.ohidl`**

```rust
@!lib("my_module_a")

@!namespace("my_module_a", "ns1.ns2.ns3.ns4.ns5")
@!ts_inject_into_module("export const PI = 3.14159;")

// class constructor overload example
@class
struct MyTest {
    a: Array<i32>;
// 构造函数需要为 native{class_name} 这个内部变量赋值
@!ts_inject_into_class("""constructor(a: Array<number> | number) {
    if (typeof a === "number") {
        this.nativeMyTest = createMyTestNum(a);
    } else {
        this.nativeMyTest = createMyTestArrayNum(a);
    }
}
""")
}

@static("MyTest")
function sum(a: i32, b: i32): i32;

function createMyTestNum(a: i32): MyTest;
function createMyTestArrayNum(a: Array<i32>): MyTest;
```

**生成`my_module_a.d.ts`**

```typescript
export function concat_str(a: string): string;
export function concat_i32(a: number): number;
export namespace ns1 {
  export interface IBase {
    getId(): string;
    setId(s: string);
  }
  export class CTest {
    constructor(id: number);
    static multiply(a: number, b: number): number;
    add(a: number, b: number): number;
  }
  export namespace ns2 {
    export namespace ns3 {
      export namespace ns4 {
        export namespace ns5 {
          export class MyTest {
            a: Array<number>;
            static sum(a: number, b: number): number;
          }
          export function createMyTestNum(a: number): MyTest;
          export function createMyTestArrayNum(a: Array<number>): MyTest;
        }
      }
    }
  }
}
```

**生成`my_module_a.ts`**

```typescript
export const PI = 3.14159;
export function concat(a: string | number): string | number {
  if (typeof a === "string") {
    return concat_str(a);
  } else {
    return concat_i32(a);
  }
}
const _taihe_native_lib = require("my_module_a");
export const concat_str = _taihe_native_lib.concat_str;
export const concat_i32 = _taihe_native_lib.concat_i32;
export namespace ns1 {
  const _taihe_native_lib = require("my_module_a");
  export interface IBase {
    add(a: number, b: number): number;
    getId(): string;
    setId(s: string);
  }
  export class CTest {
    mul(a: number, b: number): number {
      return a * b;
    }
    private nativeCTest;
    constructor(id: number) {
      this.nativeCTest = new _taihe_native_lib.ns1.CTest(id);
    }
    static multiply(a: number, b: number): number {
      return _taihe_native_lib.ns1.CTest.multiply(a, b);
    }
    add(a: number, b: number): number {
      return this.nativeCTest.add(a, b);
    }
  }
  export namespace ns2 {
    export namespace ns3 {
      export namespace ns4 {
        export namespace ns5 {
          const _taihe_native_lib = require("my_module_a");
          export const createMyTestNum =
            _taihe_native_lib.ns1.ns2.ns3.ns4.ns5.createMyTestNum;
          export const createMyTestArrayNum =
            _taihe_native_lib.ns1.ns2.ns3.ns4.ns5.createMyTestArrayNum;
          export class MyTest {
            private nativeMyTest;
            constructor(a: Array<number> | number) {
              if (typeof a === "number") {
                this.nativeMyTest = createMyTestNum(a);
              } else {
                this.nativeMyTest = createMyTestArrayNum(a);
              }
            }
            get a(): Array<number> {
              return this.nativeMyTest.a;
            }
            set a(a: Array<number>) {
              this.nativeMyTest.a = a;
            }
            static sum(a: number, b: number): number {
              return _taihe_native_lib.ns1.ns2.ns3.ns4.ns5.MyTest.sum(a, b);
            }
          }
        }
      }
    }
  }
}
```

### C++ 实现

**File: `my_module_a.ohidl 的 C++ 实现`**

```cpp
::taihe::expected<::taihe::string, ::taihe::error> concat_str(::taihe::string_view a) {
  return a + "_concat";
}

::taihe::expected<int32_t, ::taihe::error> concat_i32(int32_t a) {
  return a + 10;
}
```

**File: `my_module_a.ns1.ohidl 的 C++ 实现`**

```cpp
class CTestImpl {
  int32_t x;

public:
  CTestImpl(int32_t x) : x(x) {
    std::cout << "new ctest " << this->x << std::endl;
  }

  ~CTestImpl() {
    std::cout << "del ctest " << this << std::endl;
  }

  ::taihe::expected<float, ::taihe::error> add(int32_t a, int32_t b) {
    return a + b + this->x;
  }
};

::taihe::expected<CTest, ::taihe::error> createCTest(int32_t id) {
  return taihe::make_holder<CTestImpl, CTest>(id);
}

::taihe::expected<int32_t, ::taihe::error> multiply(int32_t a, int32_t b) {
  return a * b;
}
```

**File: `my_module_a.ns1.ns2.ns3.ns4.ns5.ohidl 的 C++ 实现`**

```cpp
::taihe::expected<int32_t sum(int32_t a, int32_t b) {
    return a * b;
}

::taihe::expected<MyTest, ::taihe::error> createMyTestNum(int32_t a) {
  ::taihe::array<int32_t> temp{a};
  return MyTest{temp};
}

::taihe::expected<MyTest, ::taihe::error> createMyTestArrayNum(::taihe::array_view<int32_t> a) {
  return MyTest{a};
}
```

**File: `my_module_b.ohidl 的 C++ 实现`**

```cpp
// Taihe 文件定义函数对应的 C++ 实现
::taihe::expected<::taihe::string, ::taihe::error> concat_str(::taihe::string_view a) {
  return a + "_concat";
}

::taihe::expected<int32_t, ::taihe::error> concat_i32(int32_t a) {
  return a + 10;
}
```

```cpp
// 实现 Taihe 文件中注入在 .d.ts 文件中声明的函数，需要在 napi register 文件中添加以下内容

// implement the inject declare in .d.ts file
// implement for inject overload functions
#include "my_module_b_functiontest.hpp"
#include "taihe/napi_runtime.hpp"

// 实现重载函数的分发
static napi_value my_module_a_concat(napi_env env,
                                     [[maybe_unused]] napi_callback_info info) {
  size_t argc = 1;
  napi_value args[1] = {nullptr};
  napi_get_cb_info(env, info, &argc, args, nullptr, nullptr);
  napi_valuetype valueType;
  napi_typeof(env, args[0], &valueType);

  switch (valueType) {
  case napi_number: {
    int32_t value0_num;
    napi_get_value_int32(env, args[0], &value0_num);
    int32_t value_num = concat_i32(value0_num);
    napi_value result_num = nullptr;
    napi_create_int32(env, value_num, &result_num);
    return result_num;
  }
  case napi_string: {
    size_t value0_len = 0;
    napi_get_value_string_utf8(env, args[0], nullptr, 0, &value0_len);
    TString value0_abi;
    char *value0_buf = tstr_initialize(&value0_abi, value0_len + 1);
    napi_get_value_string_utf8(env, args[0], value0_buf, value0_len + 1,
                               &value0_len);
    value0_buf[value0_len] = '\0';
    value0_abi.length = value0_len;
    taihe::string value0_str(value0_abi);
    ::taihe::string value_str = concat_str(value0_str);
    napi_value result_str = nullptr;
    napi_create_string_utf8(env, value_str.c_str(), value_str.size(),
                            &result_str);
    return result_str;
  }
  default:
    napi_throw_error(env, nullptr, "param type is unknown");
    return nullptr;
  }
}

// 实现重载函数入口的注册
napi_value Init_my_module_b_concat(napi_env env, napi_value exports) {
  if (::taihe::get_env() == nullptr) {
    ::taihe::set_env(env);
  }
  napi_property_descriptor desc[] = {
      {"concat", nullptr, my_module_a_concat, nullptr, nullptr, nullptr, napi_default, nullptr},
  };
  napi_define_properties(env, exports, sizeof(desc) / sizeof(desc[0]), desc);
  return exports;
}

napi_value Init(napi_env env, napi_value exports) {   // napi register 文件中的原有函数
// 在函数中添加
  // implement the inject declare in .d.ts file
  // implement for inject module const variable
  napi_value value_rate = nullptr;
  napi_create_double(env, 0.618, &value_rate);
  napi_set_named_property(env, exports, "rate", value_rate);

  // 在初始化 namespace xxx 对象与向 exports 注册 namespace xxx 对象之间调用注册 ts_inject 函数 concat 的函数
  // ... 初始化 namespace xxx 对象，例如：Init__my_module_b_functiontest(env, ns_functiontest);

  // Add register for concat function
  Init_my_module_b_concat(env, ns_functiontest);

  // ... 向 exports 注册 namespace xxx 对象，例如：Init__my_module_b_functiontest(env, exports);

}   // napi register 文件中的原有函数
```

### ArkTS-Dyn 调用

```typescript
import * as lib_b from "my_module_b"; // Use .d.ts
import * as lib_a from "../generated/proxy/my_module_a"; // Use .ts

class BaseImpl implements lib_a.ns1.IBase {
  id: string;
  constructor(id: string) {
    this.id = id;
  }
  getId(): string {
    return this.id;
  }
  setId(id: string): void {
    this.id = id;
    return;
  }
  add(a: number, b: number): number {
    return a + b;
  }
}

// Test ts inject (overload)
let res_n = lib_a.concat(1);
console.log("ts overload concat number:", res_n);
let res_s = lib_a.concat("1");
console.log("ts overload concat string:", res_s);

// Test ts inject into module
console.log("ts inject into module:", lib_a.PI);

// Test ts interface interface inject
let baseimpl_a: BaseImpl = new BaseImpl("A");
console.log("ts inject into interface interface:", baseimpl_a.add(2, 3));

// Test ts interface class inject
let ctest = new lib_a.ns1.CTest(100);
console.log("ts inject into interface class:", ctest.mul(2, 3));

// Test dts inject (overload)
let res_n_dts = lib_b.functiontest.concat(1);
console.log("dts overload concat number:", res_n_dts);
let res_s_dts = lib_b.functiontest.concat("1");
console.log("dts overload concat string:", res_s_dts);

// Test dts inject into module
console.log("inject into module dts:", lib_b.rate);

// Test ts inject constructor overload
console.log(
  "struct class static method:",
  lib_a.ns1.ns2.ns3.ns4.ns5.MyTest.sum(1, 2)
);
let new_mytest_num = new lib_a.ns1.ns2.ns3.ns4.ns5.MyTest(1);
let new_mytest_arraynum = new lib_a.ns1.ns2.ns3.ns4.ns5.MyTest([1, 2]);
console.log("ts inject overload number:", new_mytest_num.a);
console.log("ts inject overload array number:", new_mytest_arraynum.a);
```

输出结果如下：

```sh
ts overload concat number: 11
ts overload concat string: 1_concat
ts inject into module: 3.14159
ts inject into interface interface: 5
new ctest 100
ts inject into interface class: 6
dts overload concat number: 11
dts overload concat string: 1_concat
inject into module dts: 0.618
struct class static method: 2
ts inject overload number: [ 1 ]
ts inject overload array number: [ 1, 2 ]
del ctest 0x1d695640
```
