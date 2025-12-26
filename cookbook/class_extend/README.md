# 类继承

本章介绍 class 继承 class 的建议写法，通过 `@!sts_inject` 注解将 C++ 数据结构（以 `_th` 后缀标识）注入到 ETS 侧使用，确保 ETS 侧数据结构（如 `UnifiedRecord, Text, PlainText`）与 C++ 侧数据结构（如 `UnifiedRecord_th, Text_th, PlainText_th`）的正确绑定并保持继承关系的正确性。注意，C++ 数据结构（以 `_th` 后缀标识）不能在用户侧使用。

## 第一步：编写接口原型

**File: `idl/hello.taihe`**

```rust
interface UnifiedRecord_th {
    GetType(): void;
}
function CreateUnifiedRecord_noparam_th(): UnifiedRecord_th;
interface Text_th {
    GetDetails(): i32;
    SetDetails(a: i32): void;

    // 如果需要覆盖父类方法，则需要额外声明被覆盖的方法：
    // GetType(): void;
}
function CreateText_noparam_th(): Text_th;
interface PlainText_th {
    GetTextContent(): String;
    SetTextContent(a: String): void;

    // 如果需要覆盖父类方法，则需要额外声明被覆盖的方法：
    // GetDetails(): i32;
    // SetDetails(a: i32): void;
    // GetType(): void;
}
function CreatePlainText_noparam_th(): PlainText_th;

interface UnifiedData_th {
    HasType(type: String): bool;
    AddRecord(a: UnifiedRecord_th): void;
    GetRecords(): Array<UnifiedRecord_th>;
}
function CreateUnifiedData_noparam_th(): UnifiedData_th;
function CreateUnifiedData_parama_th(a: UnifiedRecord_th): UnifiedData_th;

@!sts_inject("""
export class UnifiedRecord {
    inner: UnifiedRecord_th;
    getType(): void {
        this.inner.getType();
    }
    constructor() {
        this.inner = createUnifiedRecord_noparam_th();
    }
    constructor(a: UnifiedRecord_th) {
        this.inner = a;
    }
}
export class Text extends UnifiedRecord {
    inner: Text_th;
    getDetails(): int {
        return this.inner.getDetails();
    }
    setDetails(a: int): void {
        this.inner.setDetails(a);
    }
    constructor() {
        this.inner = createText_noparam_th();
    }
    constructor(b: Text_th) {
        this.inner = b;
    }

    // 如果需要覆盖父类方法，则需要额外绑定被覆盖的方法：
    // getType(): void {
    //     this.inner.getType();
    // }
}
export class PlainText extends Text {
    inner: PlainText_th;
    getTextContent(): String {
        return this.inner.getTextContent();
    }
    setTextContent(a: String): void {
        this.inner.setTextContent(a);
    }
    constructor() {
        this.inner = createPlainText_noparam_th();
    }
    constructor(c: PlainText_th) {
        this.inner = c;
    }

    // 如果需要覆盖父类方法，则需要额外绑定被覆盖的方法：
    // getDetails(): int {
    //     return this.inner.getDetails();
    // }
    // setDetails(a: int): void {
    //     this.inner.setDetails(a);
    // }
    // getType(): void {
    //     this.inner.getType();
    // }
}
export class UnifiedData {
    inner: UnifiedData_th;
    hasType(type: string): boolean {
        return this.inner.hasType(type);
    }
    addRecord(a: UnifiedRecord) {
        this.inner.addRecord(a.inner);
    }
    getRecords() {
        let res_th: UnifiedRecord_th[] = this.inner.getRecords();
        let res: UnifiedRecord[] = new Array<UnifiedRecord>(res_th.length);
        for(let i = 0; i < res.length; i++) {
            res[i] = new UnifiedRecord(res_th[i]);
        }
        return res;
    }
    constructor() {
        this.inner = createUnifiedData_noparam_th();
    }
    constructor(x: UnifiedData_th) {
        this.inner = x;
    }
    constructor(a: UnifiedRecord) {
        this.inner = createUnifiedData_parama_th(a.inner);
    }
}
""")
```

- `_th` 类型与 ETS 类的关系
  - **`_th` 类型**：C++ 侧的数据结构，仅在 `taihe` 文件和 C++ 代码中使用，不暴露给 ETS 侧。
  - **ETS 类**：通过 `@!sts_inject` 注入的类，供 ETS 侧使用，包含对 `_th` 类型的封装。

- 方法调用规则
  - **覆盖父类方法**：若子类接口包含父类方法，ETS 侧调用子类实现。
  - **继承父类方法**：若子类接口省略父类方法，ETS 侧调用父类实现。

- 参数与返回值转换
  - **ETS 类 -> `th_` 类型**：通过 `.inner` 属性访问。
  - **`th_` 类型 -> ETS 类**：通过构造函数注入（如 `new UnifiedRecord(UnifiedRecord_th)`）。

## 第二步：完成 C++ 实现

```cpp
class UnifiedRecord_thImpl {
    public:
    UnifiedRecord_thImpl() {}

    void GetType() {
        std::cout << "function GetType in UnifiedRecord_thImpl" << std::endl;
    }
};

class Text_thImpl {
    public:
    Text_thImpl() {}

    int32_t GetDetails() {
        std::cout << "function GetDetails in Text_thImpl" << std::endl;
        return 1;
    }

    void SetDetails(int32_t a) {
        std::cout << "function SetDetails in Text_thImpl" << std::endl;
    }

    // 如果需要覆盖父类方法，则需要额外实现被覆盖的方法：
    // void GetType() {
    //     std::cout << "function GetType in Text_thImpl"  << std::endl;
    // }
};

class PlainText_thImpl {
    public:
    PlainText_thImpl() {}

    ::taihe::string GetTextContent() {
        std::cout << "function GetTextContent in PlainText_thImpl" << std::endl;
        return "GetTextContent";
    }

    void SetTextContent(::taihe::string_view a) {
        std::cout << "function SetTextContent in PlainText_thImpl" << std::endl;
    }

    // 如果需要覆盖父类方法，则需要额外实现被覆盖的方法：
    // int32_t GetDetails() {
    //     std::cout << "function GetDetails in  PlainText_thImpl" << std::endl;
    //     return 1;
    // }
    //
    // void SetDetails(int32_t a) {
    //     std::cout << "function SetDetails in  PlainText_thImpl" << std::endl;
    // }
    //
    // void GetType() {
    //     std::cout << "function GetType in  PlainText_thImpl" << std::endl;
    // }
};

class UnifiedData_thImpl {
    public:
    UnifiedData_thImpl() {}

    bool HasType(::taihe::string_view type) {
        std::cout << "function HasType in UnifiedData_thImpl" << std::endl;
    }

    void AddRecord(::hello::weak::UnifiedRecord_th a) {
        std::cout << "function AddRecord in UnifiedData_thImpl" << std::endl;
    }

    ::taihe::array<::hello::UnifiedRecord_th> GetRecords() {
        return ::taihe::array<::hello::UnifiedRecord_th>{taihe::make_holder<UnifiedRecord_thImpl, ::hello::UnifiedRecord_th>()};
    }
};

::hello::UnifiedRecord_th CreateUnifiedRecord_noparam_th() {
    return taihe::make_holder<UnifiedRecord_thImpl, ::hello::UnifiedRecord_th>();
}

::hello::Text_th CreateText_noparam_th() {
    return taihe::make_holder<Text_thImpl, ::hello::Text_th>();
}

::hello::PlainText_th CreatePlainText_noparam_th() {
    return taihe::make_holder<PlainText_thImpl, ::hello::PlainText_th>();
}

::hello::UnifiedData_th CreateUnifiedData_noparam_th() {
    return taihe::make_holder<UnifiedData_thImpl, ::hello::UnifiedData_th>();
}

::hello::UnifiedData_th CreateUnifiedData_parama_th(::hello::weak::UnifiedRecord_th a) {
    return taihe::make_holder<UnifiedData_thImpl, ::hello::UnifiedData_th>();
}
```

## 第三步：在 ets 侧使用

**File: `user/main.ets`**

```typescript
let a = new hello.UnifiedRecord();
let x1 = new hello.UnifiedData(a);
x1.addRecord(a);
let y1 = x1.getRecords();
y1[0].getType();

let b = new hello.Text();
b.getType();
b.getDetails();
let x2 = new hello.UnifiedData(b);
x2.addRecord(a);
let y2 = x2.getRecords();
y2[0].getType();
```

在使用时，声明为父类类型的函数可以接收子类对象做为入参。

如果子类数据结构定义时包含父类方法，ETS 调用时会调到子类实现，反之则调用父类实现。
