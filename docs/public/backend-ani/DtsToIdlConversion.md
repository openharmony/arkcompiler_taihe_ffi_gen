# 将已有 .d.ts 转换为 Taihe IDL 规范

本文档专门针对**为已有的 `.d.ts` 文件提供 C++ 实现**的场景，指导如何正确地将 TypeScript 类型定义转换为 Taihe IDL，并使用 Taihe 工具生成的代码模板进行实现。

## 1. 文件命名与包管理规范

### 1.1 文件命名规则

**核心原则**：一个 module 下的每个命名空间（namespace）都需要单独创建一个 `.taihe` 文件。

**命名格式**：`{module.name}.{namespace.inner}.taihe`

**具体示例**：

| .d.ts 文件                              | module                             | namespace           | .taihe 文件名                                             |
| --------------------------------------- | ---------------------------------- | ------------------- | --------------------------------------------------------- |
| `@ohos.graphics.colorSpaceManager.d.ts` | `@ohos.graphics.colorSpaceManager` | `colorSpaceManager` | `ohos.graphics.colorSpaceManager.colorSpaceManager.taihe` |
| `@ohos.multimedia.image.d.ts`           | `@ohos.multimedia.image`           | `image`             | `ohos.multimedia.image.image.taihe`                       |
| `@ohos.security.huks.d.ts`              | `@ohos.security.huks`              | `huks`              | `ohos.security.huks.huks.taihe`                           |

**建议 taihe 文件命名规则**：
* 文件名的点号分隔部分对应包名。
* 去掉 module 名称中的特殊字符 `@`。
* 将 module 名称和 namespace（如果有）用点号连接。

### 1.2 使用 @!namespace 注解映射模块

在 `.taihe` 文件的开头使用 `@!namespace` 注解指定 module 和 namespace 的映射关系：

```rust
// 文件：ohos.graphics.colorSpaceManager.colorSpaceManager.taihe
@!namespace("@ohos.graphics.colorSpaceManager", "colorSpaceManager")

// 然后定义该命名空间下的类型和函数
enum ColorSpace: i32 {
    UNKNOWN = 0,
    SRGB = 4,
}
```

**参数说明**：
* 第一个参数：module 名称（保留 `@` 前缀）。
* 第二个参数：namespace 名称（可选，省略则表示对应模块根作用域）。

## 2. TypeScript 类型到 Taihe IDL 映射表

### 2.1 基本类型映射

| TypeScript 类型 | Taihe IDL 类型         | 说明                                                          |
| --------------- | ---------------------- | ------------------------------------------------------------- |
| `void`          | `void`                 | 仅用于函数返回值                                              |
| `boolean`       | `bool`                 | 布尔值                                                        |
| `number` (整数) | `i32`                  | 默认使用 32 位有符号整数                                      |
| `number` (浮点) | `f32` 或 `f64`         | 根据精度需求选择                                              |
| `double`        | `f64`                  | 双精度浮点数                                                  |
| `string`        | `String`               | 字符串                                                        |
| `bigint`        | `@bigint Array<u64>`   | 大整数（需要使用 `@bigint` 注解）                             |
| `null`          | `@null unit`           | 无值类型（使用 `@null` 注解，注解可省略，但为了清晰建议添加） |
| `undefined`     | `@undefined unit`      | 未定义类型（需要使用 `@undefined` 注解）                      |
| `"abc"`         | `@literal("abc") unit` | 字符串字面量类型（需要使用 `@literal` 注解）                  |

### 2.2 数组与集合类型映射

| TypeScript 类型 | Taihe IDL 类型           | 注解           | 说明         |
| --------------- | ------------------------ | -------------- | ------------ |
| `Array<T>`      | `Array<T>`               | 无             | 普通数组     |
| `Uint8Array`    | `@typedarray Array<u8>`  | `@typedarray`  | 类型化数组   |
| `Uint16Array`   | `@typedarray Array<u16>` | `@typedarray`  | 类型化数组   |
| `Uint32Array`   | `@typedarray Array<u32>` | `@typedarray`  | 类型化数组   |
| `Int8Array`     | `@typedarray Array<i8>`  | `@typedarray`  | 类型化数组   |
| `Int16Array`    | `@typedarray Array<i16>` | `@typedarray`  | 类型化数组   |
| `Int32Array`    | `@typedarray Array<i32>` | `@typedarray`  | 类型化数组   |
| `Float32Array`  | `@typedarray Array<f32>` | `@typedarray`  | 类型化数组   |
| `Float64Array`  | `@typedarray Array<f64>` | `@typedarray`  | 类型化数组   |
| `ArrayBuffer`   | `@arraybuffer Array<u8>` | `@arraybuffer` | 二进制缓冲区 |
| `Record<K, V>`  | `@record Map<K, V>`      | `@record`      | 键值对映射   |

**示例：从 .d.ts 到 .taihe**

```typescript
// .d.ts
interface HuksOptions {
  properties?: Array<HuksParam>;
  inData?: Uint8Array;
}
```

转换为：

```rust
// .taihe
struct HuksOptions {
    @optional properties: Optional<Array<HuksParam>>;
    @optional inData: Optional<@typedarray Array<u8>>;
}
```

### 2.3 接口与类映射

| TypeScript 定义                  | Taihe IDL 定义                                               | 注解     | 说明       |
| -------------------------------- | ------------------------------------------------------------ | -------- | ---------- |
| `interface Foo { ... }` (无方法) | `struct Foo { ... }`                                         | 无       | 纯数据结构 |
| `interface Foo { ... }` (有方法) | `interface Foo { ... }`                                      | 无       | 接口类型   |
| `class Foo { ... }`              | `@class interface Foo { ... }` / `@class struct Foo { ... }` | `@class` | 类类型     |

**判断规则**：
* 如果 TypeScript interface 中**只有属性没有方法** → 使用 Taihe `struct`。
* 如果 TypeScript interface 中**有方法** → 使用 Taihe `interface`。
* 如果在 .d.ts 中是 `class` → 使用 `@class interface` 或 `@class struct`（根据是否有方法）。

**示例：纯数据接口**

```typescript
// .d.ts
interface ColorSpacePrimaries {
  redX: double;
  redY: double;
  greenX: double;
  greenY: double;
}
```

转换为：

```rust
// .taihe
struct ColorSpacePrimaries {
    redX: f64;
    redY: f64;
    greenX: f64;
    greenY: f64;
}
```

**示例：带方法的接口**

```typescript
// .d.ts
interface ColorSpaceManager {
  getColorSpaceName(): ColorSpace;
  getWhitePoint(): Array<double>;
  getGamma(): double;
}
```

转换为：

```rust
// .taihe
interface ColorSpaceManager {
    getColorSpaceName(): ColorSpace;
    getWhitePoint(): Array<f64>;
    getGamma(): f64;
}
```

### 2.4 枚举类型映射

| TypeScript 定义             | Taihe IDL 定义                   | 注解     | 说明       |
| --------------------------- | -------------------------------- | -------- | ---------- |
| `enum Foo { A = 1, B = 2 }` | `enum Foo: i32 { A = 1, B = 2 }` | 无       | 标准枚举   |
| `const enum Foo { ... }`    | `@const enum Foo: i32 { ... }`   | `@const` | 投影为常量 |

**示例**：

```typescript
// .d.ts
enum ColorSpace {
  UNKNOWN = 0,
  ADOBE_RGB_1998 = 1,
  DCI_P3 = 2,
  SRGB = 4,
}
```

转换为：

```rust
// .taihe
enum ColorSpace: i32 {
    UNKNOWN = 0,
    ADOBE_RGB_1998 = 1,
    DCI_P3 = 2,
    SRGB = 4,
}
```

### 2.5 联合类型映射

TypeScript 的联合类型（Union Types）需要使用 Taihe 的 `union` 类型表示。

**示例：从 .d.ts 到 .taihe**

```typescript
// .d.ts
type HuksParamValue = boolean | number | bigint | Uint8Array | null | undefined;
```

转换为：

```rust
// .taihe
union HuksParamValue {
    undefinedValue: @undefined unit;
    nullValue: @null unit;
    booleanValue: bool;
    numberValue: i32;
    bigintValue: @bigint Array<u64>;
    arrayValue: @typedarray Array<u8>;
}
```

**注意事项**：
*   如果存在 `null` 或 `undefined`，需要将它们放在其他字段前，且 `undefined` 须在 `null`。
*   如果同时存在祖先类型和子类型，需要将子类型放在祖先类型的前面以确保正确匹配。
*   `T | undefined` 可以写成 `Optional<T>`，但 `T | null` 需要使用 union。

## 3. 可选参数与属性的处理

TypeScript 中的可选参数（`?`）在 Taihe 中需要**同时使用** `@optional` 注解和 `Optional<T>` 类型。

**转换规则**：
* `a?: T` → `@optional a: Optional<T>`

**示例：可选结构体字段**

```typescript
// .d.ts
interface HuksOptions {
  properties?: Array<HuksParam>;
  inData?: Uint8Array;
}
```

转换为：

```rust
// .taihe
struct HuksOptions {
    @optional properties: Optional<Array<HuksParam>>;
    @optional inData: Optional<@typedarray Array<u8>>;
}
```

**示例：可选函数参数**

```typescript
// .d.ts
function updateSession(
  handle: number,
  options: HuksOptions,
  token?: Uint8Array
): Promise<HuksReturnResult>;
```

转换为：

```rust
// .taihe
@promise
function updateSession(
    handle: i64,
    options: HuksOptions,
    @optional token: Optional<@typedarray Array<u8>>
): HuksReturnResult;
```

## 4. 继承与实现

在 Taihe 中，TypeScript 的 `interface` 或 `class` 之间的继承与实现关系，通过以下方式表达：

*   **Struct 继承 Struct**：使用 `@extends` 字段。
*   **Interface 继承 Interface**：使用 `:` 语法。

**注意**：只允许 interface 继承 interface，或者 struct 继承 struct。如果源 TS 代码中存在 interface 继承 class 或 class 继承 interface 的情况，建议在 Taihe 中统一转换为 interface 之间的继承。

### 4.1 纯数据接口 (struct) 的继承

```typescript
// .d.ts
interface BaseDataInterface {
  id: string;
}

interface DerivedDataInterface extends BaseDataInterface {
  value: number;
}
```

转换为：

```rust
struct BaseDataInterface {
    id: String;
}

struct DerivedDataInterface {
    @extends base: BaseDataInterface;
    value: i32;
}
```

### 4.2 带方法接口 (interface) 的继承

```typescript
// .d.ts
interface BaseInterface {
  getId(): string;
}

interface DerivedInterface extends BaseInterface {
  getValue(): number;
}
```

转换为：

```rust
interface BaseInterface {
    getId(): String;
}

interface DerivedInterface: BaseInterface {
    getValue(): i32;
}
```

### 4.3 类与接口的关系

在 Taihe 中，`interface Foo: Bar` 或 `struct Foo { @extends bar: Bar; }` 的含义取决于是否有 `@class` 注解：

*   **类继承类**：如果 `Foo` 和 `Bar` 都有 `@class` 注解。
*   **类实现接口**：如果 `Foo` 有 `@class` 注解而 `Bar` 没有。
*   **接口继承接口**：如果 `Foo` 和 `Bar` 都没有 `@class` 注解。

*注意：不支持只有 `Bar` 有 `@class` 注解的情况（即接口不能继承类）。*

## 5. 异步函数的转换

TypeScript 中的异步函数主要有两种形式：`AsyncCallback<T>` 和 `Promise<T>`。在 Taihe 中推荐使用 `@async` 和 `@promise` 注解配合 `@rename` 来处理。

### 5.1 AsyncCallback 风格函数

```typescript
// .d.ts
function generateKeyItem(
  keyAlias: string,
  options: HuksOptions,
  callback: AsyncCallback<void>
): void;
```

转换为：

```rust
// .taihe
@async
function generateKeyItem(
    keyAlias: String,
    options: HuksOptions
): void;

// 如果有函数重载，由于 Taihe 不支持同名重载，需要先在 Taihe 中声明成不同名称的函数，
// 再使用 @rename 注解说明在 ArkTS 侧重命名回原名称
@async
@rename("generateKeyItem")
function generateKeyItemWithCallback(
    keyAlias: String,
    options: HuksOptions
): void;
```

**关键点**：
* 使用 `@async` 注解。
* **移除** `callback` 参数（Taihe 生成代码会自动添加）。
* 返回值类型填写原 callback 的泛型参数类型（`AsyncCallback<T>` 中的 `T`）。
* 如有重名冲突，使用 `@rename` 映射到正确的函数名。

### 5.2 Promise 风格函数

```typescript
// .d.ts
function generateKeyItem(
  keyAlias: string,
  options: HuksOptions
): Promise<void>;
```

转换为：

```rust
// .taihe
@promise
function generateKeyItem(
    keyAlias: String,
    options: HuksOptions
): void;

// 同名重载处理
@promise
@rename("generateKeyItem")
function generateKeyItemReturnsPromise(
    keyAlias: String,
    options: HuksOptions
): void;
```

**关键点**：
* 使用 `@promise` 注解。
* 返回值类型填写 Promise 的泛型参数类型（`Promise<T>` 中的 `T`）。
* 使用 `@rename` 映射原函数名。

### 5.3 处理函数重载（同名异步函数）

当 .d.ts 中同时存在同名函数的 Callback 和 Promise 版本时：

```typescript
// .d.ts
function generateKeyItem(keyAlias: string, options: HuksOptions, callback: AsyncCallback<void>): void;
function generateKeyItem(keyAlias: string, options: HuksOptions): Promise<void>;
```

在 Taihe 中需要定义两个不同名称的函数，均映射到同一个名称：

```rust
// .taihe
@async
@rename("generateKeyItem")
function generateKeyItemWithCallback(keyAlias: String, options: HuksOptions): void;

@promise
@rename("generateKeyItem")
function generateKeyItemReturnsPromise(keyAlias: String, options: HuksOptions): void;
```

**C++ 实现提示**：
可以复用相同的逻辑函数：

```cpp
void generateKeyItemImpl(taihe::string_view keyAlias, HuksOptions const& options) {
    // 实际实现逻辑
}

// 导出两次，指向同一个实现
TH_EXPORT_CPP_API_generateKeyItemWithCallback(generateKeyItemImpl);
TH_EXPORT_CPP_API_generateKeyItemReturnsPromise(generateKeyItemImpl);
```

### 5.4 带返回值的异步函数

```typescript
// .d.ts
function exportKeyItem(
  keyAlias: string,
  options: HuksOptions,
  callback: AsyncCallback<HuksReturnResult>
): void;

function exportKeyItem(
  keyAlias: string,
  options: HuksOptions
): Promise<HuksReturnResult>;
```

转换为：

```rust
// .taihe
@async
@rename("exportKeyItem")
function exportKeyItemWithCallback(
    keyAlias: String,
    options: HuksOptions
): HuksReturnResult;

@promise
@rename("exportKeyItem")
function exportKeyItemReturnsPromise(
    keyAlias: String,
    options: HuksOptions
): HuksReturnResult;
```

## 6. 静态函数和构造函数的处理

### 6.1 静态函数

在 Taihe 中，静态函数需要使用 `@static` 注解：

```typescript
// .d.ts
class Foo {
  static isKeyExist(keyAlias: string): boolean;
}
```

转换为：

```rust
// .taihe
@class interface Foo {}

@static("Foo") // 指定这是 Foo 类的静态方法
@rename("isKeyExist")  // 避免全局命名冲突，Taihe 定义名建议加前缀，@rename 映射回原名
function FooIsKeyExist(keyAlias: String): bool;
```

### 6.2 构造函数

在 Taihe 中，构造函数需要使用 `@ctor` 注解：

```typescript
// .d.ts
class Bar {
  constructor(name: string, value: number);
}
```

转换为：

```rust
// .taihe
@class interface Bar {}

@ctor("Bar")
function BarConstructor(name: String, value: i32): Bar;  // 返回类型是类本身
```

## 7. 转换检查清单

在完成 .d.ts 到 Taihe IDL 的转换后，请检查以下事项：

**文件与包管理**：
- [ ] 文件名符合 `{module.name}.{namespace.inner}.taihe` 格式。
- [ ] 使用了正确的 `@!namespace` 注解。
- [ ] 每个命名空间都有独立的 .taihe 文件。

**类型映射**：
- [ ] `double` → `f64`。
- [ ] `number` → `i32` 或 `f32`/`f64`（根据语义）。
- [ ] `string` → `String`。
- [ ] `Uint8Array` 等 → 添加了 `@typedarray` 注解。
- [ ] `ArrayBuffer` → 添加了 `@arraybuffer` 注解。
- [ ] `bigint` → 添加了 `@bigint` 注解。
- [ ] 字面量类型（如 `"abc"`） → 使用了 `unit` 类型并添加了 `@literal` 注解。

**可选参数/属性**：
- [ ] `a?: T` → `@optional a: Optional<T>`。

**接口与结构体**：
- [ ] 纯数据接口 → `struct`。
- [ ] 带方法接口 → `interface`。
- [ ] 类 → `@class interface`。
- [ ] 继承/实现关系正确使用 `:` 或 `@extends`。

**异步函数**：
- [ ] `AsyncCallback<T>` → `@async` + 移除 callback 参数。
- [ ] `Promise<T>` → `@promise` + 返回值为泛型参数。
- [ ] 函数重载 → 使用 `@rename` 映射到同名函数。

**特殊情况**：
- [ ] 同名函数重载使用了不同的 Taihe 函数名 + `@rename`。
- [ ] 需要投影为属性的方法使用了 `@get`/`@set`。
- [ ] 只读属性使用了 `@readonly` (如果适用)。
- [ ] 静态方法使用了 `@static`。
- [ ] 构造函数使用了 `@ctor`。

## 8. 常见转换错误与解决方案

| 常见错误                            | 错误原因                    | 正确做法                        |
| ----------------------------------- | --------------------------- | ------------------------------- |
| 直接写 `a?: Optional<T>`            | 缺少 `@optional` 注解       | 写成 `@optional a: Optional<T>` |
| AsyncCallback 参数保留在函数签名中  | 误以为需要手动定义          | Taihe 会自动添加，应移除        |
| Promise 函数返回值写成 `Promise<T>` | Taihe 中不需要 Promise 包装 | 直接写返回值类型 `T`            |
| 同名重载函数                        | Taihe 不支持真正的重载      | 使用不同函数名 + `@rename`      |
| `Uint8Array` 写成 `Array<u8>`       | 缺少类型注解                | 写成 `@typedarray Array<u8>`    |
| 忘记 `@!namespace` 注解             | 未指定模块映射              | 在文件开头添加注解              |
