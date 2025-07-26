# Essential Taihe

## 入门：Taihe 的基本概念

- Taihe IDL 文件使用类 C 的写法，描述了接口。

**File: idl/ohos.book.store.taihe**
```typescript
struct Book { title: String; year: i32; category: Category; }
enum Category: String { CPP = "C++", RUST = "Rust" }

function ConstructBook(title: String, year: i32, kind: Category): Book;
function PrintBook(b: Book);
```

- `taihec` 生成文件，供 API 作者填写 C++ 逻辑。
- API 作者可以使用类 STL 写法，舒适地访问 Taihe 定义的数据类型。

**File: generated/temp/ohos.book.store.impl.cpp**
```cpp
Book ConstructBook(string_view title, int32_t year, Category kind) {
  // 使用 Modern C++ 初始化结构体。
  return Book{title, year, kind};
}

void PrintBook(Book const& b) {
  printf("PrintBook: %s, year %d, kind = %s\n",
         b.title.c_str(),  // 使用 taihe::string::c_str() 获取字符串。
         b.year,
         b.category.get_value()  // 使用 enum 类型的 get_value() 获取绑定的值。
  );
}
```

- `taihec` 生成对应的 ArkTS 文件，自动将 C++ 代码投影到 ArkTS。

```sh
taihec idl/ohos.book.store.taihe -Ogenerated -Cani-bridge
```

**File (Generated): generated/ohos.book.store.ets**
```typescript
export function ConstructBook(title: string, year: int, kind: Category): Book { ... }
export function PrintBook(b: Book): void { ... }
export enum Category { CPP = "C++", RUST = "Rust" }
export interface Book { title: string; year: int; category: Category; }
class Book_inner implements Book { ... }
```

- API 消费者可以使用标准的 ArkTS 写法，消费 API。

**File: user/main.ets**
```typescript
import {ConstructBook, PrintBook, Book, Category} from "ohos.book.store";
loadLibrary("essential");

function main() {
    let book_cpp0 = ConstructBook("C++ Primer (5th ed.)", 2012, Category.CPP);
    let book_cpp1 = ConstructBook("Effective C++", 1997, Category.CPP);
    let book_rust0: Book = { title: "The Rust Programming Language", year: 2018, category: Category.RUST };
    let book_rust1: Book = { title: "Rust for Rustaceans", year: 2021, category: Category.RUST };
    let all_books: Book[] = [book_cpp0, book_cpp1, book_rust0, book_rust1];

    console.log("All books:");
    for (let i = 0; i < all_books.length; ++i) {
        PrintBook(all_books[i]);
    }
}
```

**Stdout**
```
PrintBook: C++ Primer (5th ed.), year 2012, kind = C++
PrintBook: Effective C++, year 1997, kind = C++
PrintBook: The Rust Programming Language, year 2018, kind = Rust
PrintBook: Rust for Rustaceans, year 2021, kind = Rust
```

## 入门：包，命名空间，和注解

- Taihe 的设计思想是简单明了、语言中立。因此，有很多 ArkTS 的特有能力不能在 Taihe 中原生表示出来。
- 例如，Taihe 只有“包”的概念，且包名和 Taihe IDL 文件名一一对应。
  - 举个例子，`foo.bar.baz.taihe` 对应 C++ 命名空间 `::foo::bar::baz`，对应 ArkTS 模块 `foo.bar.baz.ets`。
  - OHOS 中常见的 `@ohos.foo.bar.ets` 的写法，由于含有特殊字符 `@`，不能被 Taihe 支持。
- Taihe 使用注解机制引入语言扩展，从而更好地支持 ArkTS。例如，通过 `@namespace` 可以指定 ArkTS 中的模块和命名空间（`declare namespace MyNamespace { ... }`）

**File: idl/ohos.book.store.taihe**
```
// 将当前 Taihe 包的 ArkTS 模块名改为 `@ohos.book.store.ets`，添加 `@`
@!namespace("@ohos.book.store")

// 将当前 Taihe 包的 ArkTS 模块名改为 `@ohos.book`，本包的全部内容都放在 ArkTS 命名空间 "namespace store { ... }" 下面
@!namespace("@ohos.book", "store")

// 尽管不推荐这样写，你也可以取其他的名字。
// 例如生成一个奇怪的 ArkTS 模块 `@foo@bar@.ets`，里面的内容放在 `namespace baz { ... }` 下面。
// 注意，注解只修改 ArkTS 侧的投影，不影响 C++ 侧的代码。
// @!namespace("@foo@bar@", "baz")
```

- Taihe 的注解非常灵活
  - `@!foobar` 添加注解到**当下的词法空间**下，而 `@foobar` （注意，没有感叹号）将注解添加到**下一个元素**中。
  - 例如，`@foobar struct Foo {}` 等价于 `struct Foo { @!foobar }`，都是在给 `struct Foo` 添加注解。
  - 注解可以有参数，例如 `@foobar("baz")` 或 `@foobar(1, "baz")`
  - 无参数时，括号可以省略，例如 `@foobar()` 等同于 `@foobar`

## 入门：函数，入参，和返回值

- Taihe 支持多种多样的类型，以及类型的组合
  - `i8`, `i16`, `i32`, `i16`: 有符号数，对应 ArkTS 的 `byte` 等类型。注意，`u` 开头的无符号数不被 ArkTS 支持，因此不建议使用。
  - `f32`, `f64`: 对应 ArkTS 的 `float` 和 `double` 类型
  - `bool`
  - `union`: 表示多个类型间的选择，对应 ArkTS 投影 `type Foo = Bar | Baz;`
  - `Optional<T>`: 表示可空的对象，对应 ArkTS 投影 `foo: Bar | undefined`
  - `Array<T>`: 表示数组，对应 ArkTS 投影 `foo: T[]`
  - `@arraybuffer Array<u8>`: 表示 ArkTS 的 `ArrayBuffer`（本文未给出示例），是 `u8` 的特殊用法。
  - `@typedarray Array<u8>`: 表示 ArkTS 的 `Uint8Array`
  - `@bigint Array<u64>`: 表示 ArkTS 的 `BigInt`
  - `(arg: ArgT) => RetT` 表示回调函数，对应 ArkTS 投影 `(arg: ArgT) => RetT`

- 让我们用高级特性举个例子。在 Taihe IDL 文件中引入这些代码

**File: idl/ohos.book.store.taihe**
```typescript
union MapOption {
  one_book: Book;
  many_book: Array<Book>;
}
// 数组，union 和 HashMap。本函数接收一本书或多本书，返回书名所对应的出版年份。
function MapBookToYear(opt: MapOption): @record Map<String, i32>;

// 回调函数和可选参数。本函数接收一个可选的过滤器回调，Print 函数将只打印通过过滤的书。
function PrintBooksWithFilter(all_books: Array<Book>, filter: Optional<(b: Book) => bool>);
```

- 对应的 ArkTS 投影如下

**File (Generated): generated/ohos.book.store.ets**
```typescript
// Taihe 使用联合体，支持传入多种类型
export type MapOption = Book | (Book[]);
function MapBookToYear(opt: MapOption): Record<string, int>;

// Taihe 支持类型的嵌套，例如 Optional 嵌套 Callback 嵌套 Book
function PrintBooksWithFilter(all_books: (Book[]), filter: (((arg_0: Book) => boolean) | undefined)): void;
```

- 使用 C++ 完成后续逻辑的开发

**File: author/src/ohos.book.store.impl.cpp**
```cpp
map<string, int32_t> MapBookToYear(MapOption const& opt) {
  map<string, int32_t> ret;
  // 通过 get_tag() 判断类型，通过 get_xxx_ref() 获得对应的值。
  if (opt.get_tag() == MapOption::tag_t::one_book) {
    Book const& book = opt.get_one_book_ref();
    ret.emplace(book.title, book.year);
  } else {
    // 使用标准的 STL 风格访问 many_books 数组。
    for (auto const& book : opt.get_many_books_ref()) {
      ret.emplace(book.title, book.year);
    }
  }
  return ret;
}

void PrintBooksWithFilter(array_view<Book> all_books,
                          optional_view<callback<bool(Book const&)>> filter) {
  for (auto& book : all_books) {
    bool should_print = true;
    // 判断 Optional 是否有值。
    if (filter) {
      // 使用 (*filter) 获取 filter 背后的 callback，并调用 callback。
      should_print = (*filter)(book);
    }

    // Taihe 导出的函数和普通函数没什么差别，可以随意调用。
    if (should_print) PrintBook(book);
  }
}
```

- 编写测试的 `main.ets`，执行测试

**File: user/main.ets**
```typescript
    console.log("Book mapping:");
    for (let pair of MapBookToYear(all_books)) {
        console.log("Year " + pair[1] + ": " + pair[0]);
    }

    console.log("Books of Rust:");
    // 写一个 lambda，只对 Rust 书籍返回 true
    PrintBooksWithFilter(all_books, (b: Book) => { return b.category == Category.RUST; });
```

**Stdout**
```
Book mapping:
Year 2012: C++ Primer (5th ed.)
Year 2018: The Rust Programming Language
Year 2021: Rust for Rustaceans
Year 1997: Effective C++

Books of Rust:
PrintBook: The Rust Programming Language, year 2018, kind = Rust
PrintBook: Rust for Rustaceans, year 2021, kind = Rust
```

- 作为函数参数时，不同的类型有不同的语义和内存管理方式

  | 类型       | 例子        | 作为函数参数             | 作为函数返回值          |
  |------------|-------------|--------------------------|-------------------------|
  | 基础类型   | `i8`        | 从 ArkTS 复制到 C++      | 从 C++ 复制到 ArkTS     |
  | 复合类型   | `struct`    | 从 ArkTS 复制到 C++      | 从 C++ 复制到 ArkTS     |
  | 容器类型   | `Array`     | 从 ArkTS *借用* 给 C++   | 从 C++ 复制到 ArkTS     |
  | 接口类型   | `interface` | 从 ArkTS 找到 C++ 指针   | 将 C++ 指针包装给 ArkTS |
  | 不透明类型 | `Opaque`    | 按 `ani_object` 处理     | 按 `ani_object` 处理    |

- 需要注意的是，对于容器类型（例如 `Array`），Taihe 以**传只读引用**的形式在 ArkTS 和 C++ 间传递。
  - 换言之，开发者可以在 C++ 中读取参数中容器的值，但不能修改。**C++ 修改 ArkTS 的容器值，尽管可能编译通过，但属于未定义行为。**
  - 类似地，将 C++ 容器返回给 ArkTS 后，若 ArkTS 侧修改了数据，则这部分修改也只对 ArkTS 可见。

## 接口：将 C++ 对象绑定到 ArkTS

- Taihe 的函数是无状态的。传入参数，传出返回值，仅此而已。
- Taihe 使用 `interface` 管理状态。复用 C++ 的“类”，来将数据和函数关联在一起。ArkTS 侧的投影会复用 C++ 对象的状态。
- Taihe 的 `interface` 有明确的约束，只支持存放方法，不支持静态函数、构造器、属性。
  - 注：`interface` 不支持构造器，所以需要使用静态函数 + 返回对象的方式创建 `interface`
- Taihe 基于注解机制，将约束严格的 `interface` 投影到具有丰富能力的 ArkTS `interface` 或 `class` 上。
  - `@class`: 在 ArkTS 中生成 `class`，而非 `interface`
  - `@ctor`: 生成构造器（仅当 `@class` 时有效）
  - `@static`: 生成静态方法（仅当 `@class` 时有效）
  - `@get` 和 `@set`: 生成属性，或只有 `@get` 无 `@set` 时生成 `readonly` 属性

**File: idl/ohos.book.store.taihe**
```typescript
// 将 Bookstore 生成为 ArkTS 的 `class`。不加此注解时生成 `interface`。
@class
interface Bookstore {
  addBook(book: Book, price: f64, count: i32);
  saleBook(book: Book);

  // 使用 @get 或 @set 来替代属性。
  @get getDiscount(): f64;
  @set setDiscount(percent: f64);

  // 使用 @get 替代只读属性。
  @get getTotalSales(): f64;
}

// 使用 @ctor 给 Bookstore 添加构造器
@ctor("Bookstore")
function CreateBookstore(): Bookstore;

// 使用 @static 给 Bookstore 添加静态方法。
@static("Bookstore")
function SayHello();
```

**File: idl/ohos.book.store.ets**
```typescript
export class Bookstore {
    // Taihe 内部使用两个指针管理 Native 对象。
    private _vtbl_ptr: long;
    private _data_ptr: long;
    private constructor(_vtbl_ptr: long, _data_ptr: long) {
        this._vtbl_ptr = _vtbl_ptr;
        this._data_ptr = _data_ptr;
    }

    constructor() { ... }
    static SayHello(): void { ... }
    addBook(book: Book, price: double, count: int): void { ... }
    saleBook(book: Book): void { ... }
    get discount(): double { ... }
    set discount(percent: double) { ... }
    get totalSales(): double { ... }
}
```

- 接下来实现 C++ 部分。
  - Taihe 标准库提供了 `make_holder<ImplT, IfaceT...>` 来将 C++ 类绑定到 Taihe 接口
  - Taihe 标准库提供了 `set_error`, `set_business_error` 来抛异常。
  - 全部的状态都保存在 C++ 中。

**File: author/src/ohos.book.store.impl.cpp**
```cpp
class BookstoreImpl {
  double m_discount_percent = 0.0f;
  double m_total_sales = 0.0f;
  std::unordered_map<std::string, std::pair<double, int32_t>> m_books = {};

public:
  void addBook(Book const& book, double price, int32_t count) {
    m_books.emplace(std::string{book.title}, std::make_pair(price, count));
    PrintBook(book);
    printf("addBook: price = %lf, count = %d\n", price, count);
  }

  void saleBook(Book const& book) {
    auto iter = m_books.find(std::string{book.title});
    auto price = iter->second.first;
    auto& count = iter->second.second;
    if (count == 0) {
      // 使用 taihe::set_business_error 抛异常。
      taihe::set_business_error(1, book.title + " has been sold out");
      return;
    }

    count -= 1;
    m_total_sales += price * (1 - m_discount_percent / 100);

    printf("saleBook: price = %lf, count = %d, title = %s\n", price, count,
           book.title.c_str());
  }

  double getDiscount() {
    return m_discount_percent;
  }

  void setDiscount(double percent) {
    m_discount_percent = percent;
  }

  double getTotalSales() {
    return m_total_sales;
  }
};

Bookstore CreateBookstore() {
  return make_holder<BookstoreImpl, Bookstore>();
}

void SayHello() {
  printf("Welcome to my book store!\n");
}
```

- 编写测试的 `main.ets`，执行测试
- 先添加书进去，两本书，单价 20 元
- 接着不断卖书，并调整折扣。
- 书卖光了，抛异常。

**File: user/main.ets**
```typescript
    Bookstore.SayHello();
    let store = new Bookstore();
    store.addBook(book_rust0, 20.0, 2);

    store.discount = 50; // 打五折
    store.saleBook(book_rust0);
    console.log("Total sales: " + store.totalSales)
    store.discount = 20; // 打八折
    store.saleBook(book_rust0);
    console.log("Total sales: " + store.totalSales)

    try {
        // 卖光了，不能再卖了。
        store.saleBook(book_rust0);
    } catch (error) {
        console.log("error: " + error);
    }
```

**Stdout**
```
Welcome to my book store!
PrintBook: The Rust Programming Language, year 2018, kind = Rust
addBook: price = 20.000000, count = 2
saleBook: price = 20.000000, count = 1, title = The Rust Programming Language
Total sales: 10
saleBook: price = 20.000000, count = 0, title = The Rust Programming Language
Total sales: 26
error: Error: The Rust Programming Language has been sold out
```

## 漫谈：Taihe 的设计目标和语言能力

Taihe 以语言中立为设计目标。尽管通过注解可以在 ArkTS 中实现高级特性，但核心语言只提供面向 API 的、受限的语言能力：

  - `function`: 静态函数
    - 支持入参和返回。
    - **不支持**重载，也就是无法将多个函数实现绑定到同一个名字下。但是，可以使用 `@overload` 在 ArkTS 下实现语言扩展能力。
  - `interface`: 接口，将 Native 状态绑定到外部
    - 支持方法。
    - 支持多接口，以及接口间的依赖。
    - **不支持**静态方法和构造器，使用函数返回值代替。
    - **不支持**属性，使用 `get` 或 `set` 方法代替。
  - **不支持** `class`
    - Taihe 对外不暴露 `class` 的概念，尽管 C++ 需要使用 `make_holder` 将 C++ `class` 绑定到 Taihe `interface`。
    - Taihe 对外不暴露类继承的概念，只有接口依赖和实现。换言之，在 C++ 语境下，Taihe `interface` 均为虚基类，Taihe `interface` 中的方法均为纯虚函数。

Taihe 以温和改良为设计目标。新增的 Taihe 绑定可以与现有 C++ 代码和谐共存。

  - Taihe 对 API 作者的限制非常少，只要求 API 作者在二进制层面兼容 Taihe：
    - 需要导入生成的 `hpp` 文件和 Taihe 系统库，从而使用 Taihe ABI 兼容的数据结构
    - 需要展开 `TH_EXPORT_CPP_API_foobar` 宏，从而将 API 作者侧的函数导出到 Taihe ABI
    - 需要调用 `taihe::make_holder`，从而将 API 作者侧的 `interface` 实现导出到 Taihe ABI
  - 不同于传统的 IDL 框架，Taihe 有很强的灵活度：
    - 可以在存量 C++ 代码中使用 `TH_EXPORT_CPP_API_foobar` 导出兼容 Taihe 的现有函数
    - 可以在存量 C++ 代码中使用 `make_holder` 导出兼容 Taihe 的任意类。
    - 可以在存量 C++ 代码中混合 Taihe 对象，因为 C++ 中的 Taihe 的容器和 `interface` 实现，都是完全合法的 C++ 对象。
  - 因此，尽管 `taihec` / `run-test` 等工具会帮助 API 作者创建代码骨架，但并不意味着 API 作者要完全依赖该骨架：
    - 可以对 C++ 源文件任意起名。
    - 可以对 C++ 类任意起名，或是选择性地 `make_holder`，动态切换接口背后的 C++ 实现。
    - 可以对 C++ 函数任意起名，甚至使用函数模板。

**File: example.cpp**
```cpp
// 定义 C++ 函数模板
template<bool endl>
void print_str(taihe::string_view pstr) {
  if (endl) {
    std::cout << pstr.c_str() << std::endl;
  } else {
    std::cout << pstr.c_str() << std::flush;
  }
}

// 将模板以不同的参数展开，并导出为不同的名字。
TH_EXPORT_CPP_API_print(print_str<false>);
TH_EXPORT_CPP_API_println(print_str<true>);
```

## 进阶：结构体的高级特性

- Taihe 的 `struct` 为值类型，不支持 C++ 的继承。为了简化 ArkTS 的编写，Taihe 提供了 `@extends` 写法，用组合的方式实现继承。
- 此外，`struct Foo` 默认生成的是 `interface Foo`（用于接受 ArkTS 用户的传入）和 `class Foo_inner implements Foo`（用于 C++ 返回值的传出）。可以使用 `@class` 规避 `interface Foo`，直接生成 `class Foo` 保证 ArkTS 的兼容性。

**File: idl/ohos.book.store.taihe**
```typescript
@class
struct RustBook {
  @extends base: Book;
  rust_version: i32;
}

@class
struct CppBook {
  @extends base: Book;
  compiler: String;
}

union CppOrRustBook {
  rust: RustBook;
  cpp: CppBook;
}

function PrintBookAdvanced(book: CppOrRustBook);
```

- 对应的 ArkTS 投影如下

**File (Generated): generated/ohos.book.store.ets**
```typescript
export class RustBook implements Book {
    title: string;
    year: int;
    category: Category;
    rust_version: int;
    // [...]
}

export class CppBook implements Book {
    title: string;
    year: int;
    category: Category;
    compiler: string;
    // [...]
}

export type CppOrRustBook = RustBook | CppBook;
export function PrintBookAdvanced(book: CppOrRustBook): void { ... }
```


- 使用 C++ 完成后续逻辑的开发

**File: author/src/ohos.book.store.impl.cpp**
```cpp
void PrintBookAdvanced(CppOrRustBook const& book) {
  if (book.holds_rust()) {
    RustBook the_book = book.get_rust_ref();
    PrintBook(the_book.base);
    printf("Hint: use Rust edition %d to try.\n", the_book.rust_version);
  }
  if (book.holds_cpp()) {
    CppBook the_book = book.get_cpp_ref();
    PrintBook(the_book.base);
    printf("Hint: use %s to compile.\n", the_book.compiler.c_str());
  }
}
```

- 编写测试的 `main.ets`，执行测试

**File: user/main.ets**
```typescript
    PrintBookAdvanced(new RustBook("The Rust Programming Language", 2018, Category.RUST, 2018));
    PrintBookAdvanced(new CppBook("Effective C++", 1997, Category.CPP, "Borland C++"));
```

**Stdout**
```
PrintBook: The Rust Programming Language, year 2018, kind = Rust
Hint: use Rust edition 2018 to try.
PrintBook: Effective C++, year 1997, kind = C++
Hint: use Borland C++ to compile.
```


## 进阶：接口和继承

- Taihe 的 `interface` 默认生成 ArkTS 的 `interface`，在使用 `@class` 修饰时，生成 ArkTS 的 `class`。
- Taihe 支持 ArkTS `class` 或 `interface` 继承一个或多个 ArkTS `interface`。
- Taihe 支持 ArkTS 内的基类 / 子类互转，以及 C++ 内的基类 / 子类互转。
- 但是，**Taihe 不支持跨语言的互转**。例如，下面的代码片段展示了各种转换的情况。

**File: example.taihe**
```typescript
interface Base {}
// 接口 Derived 继承自 Base
interface Derived : Base {}

function UseBase(b: Base);
function UseDerived(d: Derived);
function GetBase(): Base;
function GetDerived(): Derived;
```

**File: example.ets**
```typescript
let derived_as_base: Base = GetDerived() as Base; // 正确，允许 ArkTS 内互转。
UseBase(derived_as_base); // 错误！将 Derived 类型传入 Native 的 Base 类型。
UseDerived(derived_as_base as Derived); // 正确，无跨语言转换。
```

- 常见的情况是，用继承来代替 Sum Type，从而返回多种类型的组合。这种情况下，更适合使用 `union` 来表示。

**File: example.taihe**
```typescript
interface Base {}
interface D1 : Base {}
interface D2 : Base {}
interface D3 : Base {}

// ======== 符合直觉，但实质错误的写法 ========
// Make 的 C++ 逻辑：根据 kind 在 D1, D2, D3 之间选择某一个。
function Make(kind: i32): Base;  // 错误！返回 Base 类型依赖跨语言转换，导致类型混淆。
function Use(b: Base);           // 错误！需要将 ArkTS 类型转换为 Base 类型，导致类型混淆。

// ======== 正确写法 ========
union D123 {
  d1: D1;
  d2: D2;
  d3: D3;
}
function Make(kind: i32): D123;  // 正确，明确说明返回的类型。
function Use(d: D123);           // 正确，明确说明传入的类型。
```

## 进阶：接口和多继承

- Taihe 支持同时实现多个接口。例如，我们定义高级类型 `FancyBook`：

**File: idl/ohos.book.store.taihe**
```typescript
// 基础接口：单价
interface HasPrice { @get getPrice(): f64; }
// 基础接口：折扣，折扣依赖单价
interface HasDiscount : HasPrice { @get getDiscount(): f64; }
// 基础接口：出版商
interface HasPublisher { @get getPublisher(): String; }
// 衍生类：具有出版商和折扣
@class interface FancyBook: HasPublisher, HasDiscount { @get getTitle(): String; }
@ctor("FancyBook") function MakeFancyBook(): FancyBook;
```

- 对应的 ArkTS 投影如下：

**File (Generated): generated/ohos.book.store.ets**
```typescript
export interface HasPrice {
    get price(): double;
}
export interface HasDiscount extends HasPrice {
    get discount(): double;
}
export interface HasPublisher {
    get publisher(): string;
}
export class FancyBook implements HasPublisher, HasDiscount {
    get title(): string { ... }
    get publisher(): string { ... }
    get discount(): double { ... }
    get price(): double { ... }
}
```

- 使用 C++ 完成后续逻辑的开发

**File: author/src/ohos.book.store.impl.cpp**
```cpp
FancyBook MakeFancyBook() {
  // 内部临时写一个类吧！只要函数都具备，就可以转换到 Taihe 对象。
  struct FancyRustBook {
    string getPublisher() {
      return "No Starch Press";
    }

    string getTitle() {
      return "The Rust Programming Language";
    }

    double getDiscount() {
      return 0.0 /* No discount, sorry.*/;
    }

    double getPrice() {
      return 50.0;
    }
  };

  // 把这个类包装为 Taihe 对象。注意，这里的 class 只实现了与之相关的 FancyBook 接口。
  return make_holder<FancyRustBook, FancyBook>();
}
```

- 编写测试的 `main.ets`，执行测试

**File: user/main.ets**
```typescript
    let fancy_book = new FancyBook();
    console.log(`Got a fancy book: ${fancy_book.title} by ${fancy_book.publisher},` +
                ` costs \$${fancy_book.price} with discount ${fancy_book.discount}%`);
```

**Stdout**
```
Got a fancy book: The Rust Programming Language by No Starch Press, costs $50 with discount 0%
```

## 进阶：函数的重载和异步化

- Taihe 使用 `@overload`，将不同参数的 Taihe `function` 绑定到相同的名字上。需要注意，绑定的名字和参数列表需符合 ArkTS 语言的约束。

**File: example.taihe**
```typescript
@overload("SaveBook")
function SaveBookToInternet(url: String);
@overload("SaveBook")
function SaveBookToFile(p: Path);
```

对应的 ArkTS 投影如下：

**File (Generated): generated/example.ets**
```typescript
export function SaveBook(url: string): void {
    return SaveBookToInternet_inner(url);
}
export function SaveBook(p: Path): void {
    return SaveBookToFile_inner(p);
}
```

- Taihe 使用 `@gen_promise` 和 `@gen_async` 注解，将同步函数封装为异步版本。
  类似于 `@overload`，可以将 `AsyncCallback` 和 `Promise` 版本的函数绑定到相同的名字。

**File: example.taihe**
```typescript
@gen_async("uploadBook")
@gen_promise("uploadBook")
function uploadBook(b: Book): String;
```

**File (Generated): generated/example.ets**
```typescript
export function uploadBook(b: Book): string {
    return uploadBook_inner(b);
}
export function uploadBook(b: Book): Promise<string> {
    return new Promise<string>((resolve: (data: string) => void, reject: (err: Error) => void): void => {
        taskpool.execute((): string => { return uploadBook_inner(b); })
        .then((ret: Any): void => {
            resolve(ret as string);
        })
        .catch((ret: Any): void => {
            reject(ret as Error);
        });
    });
}
export function uploadBook(b: Book, callback: (err: Error | null, data?: string) => void): void {
    taskpool.execute((): string => { return uploadBook_inner(b); })
    .then((ret: Any): void => {
        callback(null, ret as string);
    })
    .catch((ret: Any): void => {
        callback(ret as Error);
    });
}
```

- Taihe 使用 `@on_off`，从而兼容 ArkTS 特殊的值类型重载。该注解会自动拆解 `on` 和 `off` 后续的字符串，然后用作接口派发。

**File: example.taihe**
```typescript
@on_off function onBookSold();
@on_off function onNewBook();
```

对应的 ArkTS 投影如下：

**File (Generated): generated/example.ets**
```typescript
native function onBookSold_inner(): void;
native function onNewBook_inner(): void;
export function on(type: string): void {
    switch(type) {
        case "bookSold": return onBookSold_inner();
        case "newBook": return onNewBook_inner();
        default: throw new Error(`Unknown type: ${type}`);
    }
}
```

## 逃逸通道：ArkTS 代码注入

- Taihe 将生成代码不上库作为设计目标。但全盘兼容 ArkTS 的复杂语言特性并非 Taihe 的设计目标。
- 在一些情况下，需要插入 ETS 代码，在高级语言侧完成复杂逻辑。
- Taihe 提供 `@sts_inject` 等函数，用于在生成的代码中插入 ETS 文本片段。
  - `@!sts_inject` 在 ArkTS 模块文件的开头注入代码，一般用于添加自己的函数。
  - `@!sts_inject_into_interface` 在 Taihe `interface` 内生效，可以在 ArkTS 投影中的 `interface` 内注入自己的属性或方法。
  - `@!sts_inject_into_class` 同样在 Taihe `interface` 内生效，可以在 ArkTS 投影中的 `class` 内注入自己的属性或方法。

**File: example.taihe**
```typescript
@!sts_inject("// Inside the main source file")
interface Foo {
  @!sts_inject_into_class("// In `class Foo_impl`")
  @!sts_inject_into_interface("// In `interface Foo`")
}
```

**File (Generated): generated/example.ets**
```typescript
// Inside the main source file
export interface Foo {
    // In `interface Foo`
}
class Foo_inner implements Foo {
    // In `class Foo_impl`
    // [...]
}
```

## 逃逸通道：ANI 代码注入

- 类似于 ArkTS 代码注入，Taihe 支持引入 ANI 代码，从而在 C++ 侧访问 ArkTS 对象：
  - `Opaque` 类型：对应 ArkTS 的 `Any` 类型、ANI 的 `ani_object`，可以存放任意可空引用类型。允许 `Opaque` 类型和其他类型相组合。
  - `@sts_this` 注解：在类中适用，获得与 Taihe 对象相绑定的 ArkTS 类的 `ani_object`
  - `ani_env taihe::get_env()`：返回 `ani_env` 指针

**File: idl/ohos.book.store.taihe**
```typescript
function is_string(s: Opaque): bool;
function get_objects(): Array<Opaque>;
```

- 对应的 ArkTS 投影如下：

**File (Generated): generated/ohos.book.store.ets**
```typescript
export function is_string(s: Any): boolean { ... }
export function get_objects(): (Any[]) { ... }
```

- 使用 C++ 完成后续逻辑的开发

**File: author/src/ohos.book.store.impl.cpp**
```cpp
bool IsString(uintptr_t s) {
  ani_boolean res;
  ani_class cls;
  ani_env* env = get_env();
  env->FindClass("std.core.String", &cls);
  env->Object_InstanceOf((ani_object)s, cls, &res);
  return res;
}

array<uintptr_t> GetStringArray() {
  ani_env* env = get_env();
  // 首个元素为字符串 "AAA"
  ani_string ani_arr_0;
  env->String_NewUTF8("AAA", 3, &ani_arr_0);
  // 接下来的元素为 undefined
  ani_ref ani_arr_1;
  env->GetUndefined(&ani_arr_1);
  return array<uintptr_t>({(uintptr_t)ani_arr_0, (uintptr_t)ani_arr_1});
}
```

- 编写测试的 `main.ets`，执行测试

**File: user/main.ets**
```typescript
    const s = "hello";
    const i = 233;
    console.log(`${s} is string? ${IsString(s)}`);
    console.log(`${i} is string? ${IsString(i)}`);
    console.log(`GetStringArray = ${GetStringArray()}`);
```

**Stdout**
```
hello is string? true
233 is string? false
GetStringArray = AAA,undefined
```

## 常见问题

- Unhandled exception: std.core.LinkerUnresolvedMethodError
  - 检查 `user/main.ets`，是否遗漏了 `loadLibrary("<your-lib-name-here>")`
  - 在使用 `run-test` 工具时，目录名就是 `loadLibrary` 需要填写的名字

- `union` 类型判断错误
  - `union` 的类型判断基于 ArkTS 的类型系统，根据分支的先后顺序判断
  - 例如 `union { d: Derived; b: Base; }` 可以成功区分基类和子类，但交换顺序则无法判断成功，因为首次判断基类即成功返回。
  - 类似地，`union` 中存在 `Opaque` 必须放在最后，且不允许定义多个 `Opaque`
  - 此外，`union` 受到 ArkTS 类型擦除机制的约束，因此无法区分泛型。
