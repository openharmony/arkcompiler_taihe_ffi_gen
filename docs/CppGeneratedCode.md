# Taihe ABI 及 C++ 层代码解析

## 原始 IDL 文件内容

```rust
// File: example/idl/my.package.taihe
struct Data {
    a: i32;
    b: String;
}
union Result {
    ok: i32;
    err: String;
}
interface IFoo {
    init(): void;
}
interface IBar: IFoo {
    process(data: Data): Result;
}
function processWithBar(bar: IBar, data: Data): Result;
```

## 生成的 ABI 层代码

当 Taihe 工具链处理 `my.package.taihe` 这个 IDL 文件后，会在指定的输出目录生成一系列文件。这些文件可以被清晰地划分为 ABI 层和 C++ 层。

以下是生成文件的结构树及其功能简介：
```
generated/
├── include/
│   ├── my.package.Data.abi.{0,1,2}.h      // ABI 层：结构体 Data 的分阶段定义
│   ├── my.package.Result.abi.{0,1,2}.h    // ABI 层：联合体 Result 的分阶段定义
│   ├── my.package.IFoo.abi.{0,1,2}.h      // ABI 层：接口 IFoo 的分阶段定义
│   ├── my.package.IBar.abi.{0,1,2}.h      // ABI 层：接口 IBar 的分阶段定义
│   ├── my.package.abi.h                   // ABI 层：聚合头文件
│   ├── my.package.Data.proj.{0,1,2}.hpp   // C++ 层：结构体 Data 的 C++ 投影
│   ├── my.package.Result.proj.{0,1,2}.hpp // C++ 层：联合体 Result 的 C++ 投影
│   ├── my.package.IFoo.proj.{0,1,2}.hpp   // C++ 层：接口 IFoo 的 C++ 投影
│   ├── my.package.IBar.proj.{0,1,2}.hpp   // C++ 层：接口 IBar 的 C++ 投影
│   ├── my.package.proj.hpp                // C++ 层：聚合通用头文件（供接口实现方和用户使用）
│   ├── my.package.user.hpp                // C++ 层：供接口【消费方】使用的头文件
│   └── my.package.impl.hpp                // C++ 层：供接口【发布方】使用的头文件
├── src/
│   └── my.package.abi.c                   // ABI 层：接口 IID 等符号的定义
└── temp/
    └── my.package.impl.cpp                // C++ 层：为发布方提供的实现模板
```

- **ABI 层 (`.abi.h`, `.abi.c`)**：定义了所有类型的 C 语言内存布局、函数签名和接口 ID。这是所有上层代码（包括 C++ 和其他语言）的共同基础。
- **C++ 层 (`.hpp`, `.cpp`)**：
    - `proj.hpp` 文件：包含了所有公开类型（结构体、接口等）的 C++ 封装，是接口实现方和使用方都需要引用的基础文件。
    - `user.hpp` 文件：除了 `proj.hpp` 的内容外，还包含了全局函数的 C++ 包装，专供函数的【调用者】使用。
    - `impl.hpp` 文件：提供了导出全局函数的宏，专供函数的【实现者】使用。
    - `impl.cpp` 文件：一个自动生成的实现骨架，帮助开发者快速开始编写接口的实现代码。

值得注意的是，头文件被拆分为 `*.{0,1,2}.h/hpp` 的形式，这是用于解决 C/C++ 中类型间循环依赖问题。
- `*.0.h/hpp`: 包含类型的前向声明，`*.proj.0.hpp` 中还会包含 `taihe::as_abi` 模板的特化，用于表示 ABI 类型和 C++ 类型之间的映射关系。
- `*.1.h/hpp`: 包含类型本身的完整定义，以及接口间的动态、静态转换方法等。但不包含接口成员方法的声明和定义。
- `*.2.h/hpp`: 包含了接口的所有成员方法，并且会递归地包含该类型所依赖的其他类型（如结构体和联合体中成员的类型、接口成员方法的参数和返回值的类型等）的全部成员方法。

## 运行时调用链示例

理解运行时调用链是掌握 Taihe 工作原理的关键。

### 场景一：创建对象并调用方法

**代码**:
```cpp
using namespace my::package;

// 创建对象
IBar bar = taihe::make_holder<BarImpl, IBar>();
// 调用方法
bar->process(data);
```

**调用链**:
1.  **对象创建 (`make_holder`)**：（需结合 `runtime/include/taihe/object.hpp`）
    a. `taihe::make_holder<BarImpl, IBar>()` 会调用 `taihe::impl_holder<BarImpl, IBar>` 的静态工厂方法 `make()`。这会使得在编译期生成一个 `rtti` 编译期常量，其中包含了 `BarImpl` 的类型信息，如版本信息、析构函数、Interface ID Map（从所有实现的接口 ID 到相应虚表指针的映射关系）等。
    b. 接下来，`make()` 方法会在堆上申请内存，创建一个 `taihe::data_block<BarImpl>` 对象，该对象内部同时包含 `DataBlockHead` 数据和 `BarImpl` 的实例。`BarImpl` 的构造函数会被调用。
    c. 接下来会调用 `tobj_init` 函数来初始化 `DataBlockHead`，这会将对象的引用计数设置为 1，并将 `rtti` 的地址存入 `DataBlockHead` 的 `rtti_ptr` 中。
    d. `taihe::impl_holder<BarImpl, IBar>` 会持有指向该 `taihe::data_block<BarImpl>` 对象的指针（`data_ptr`）。
    e. 最后，`taihe::impl_holder<BarImpl, IBar>` 被隐式转换为 `IBar`，这会根据前者的编译期信息，找到 `BarImpl` 对应于 `IBar` 接口的虚表指针（`vtbl_ptr`），并和 `data_ptr` 一起构成一个 `IBar` 对象。转换后的对象只能调用 `IBar` 接口上定义的方法，而丢失了 `BarImpl` 类本身的具体实现细节。

2.  **方法调用 (`bar->process`)**：
    a. C++ 代码 `bar->process(data)` 会调用 `weak::IBar::virtual_type` 中定义的 `process` 方法。
    b. 这个 C++ 包装方法通过 `into_abi` 将 C++ 类型的 `data` 转换为 ABI 类型，然后调用 ABI 层的辅助函数 `my_package_IBar_process_f`。
    c. `my_package_IBar_process_f` 通过 `bar` 的 `vtbl_ptr` 取得 `ftbl_ptr_0`（`IBar` 的函数表），并调用其中的 `process` 函数指针。
    d. 这个函数指针指向 `weak::IBar::methods_impl<BarImpl>::process` 这个静态模板方法，该模板方法是之前在创建 `taihe::impl_holder<BarImpl, IBar>` 时自动实例化出来，并注册到虚函数表中的。
    e. `methods_impl<BarImpl>::process` 是连接 ABI 和 C++ 实现的最后一环。它接收 ABI 类型的参数并通过 `taihe::from_abi` 转换回 C++ 类型，使用 `taihe::cast_data_ptr<BarImpl>` 将通用的 `data_ptr` 安全地转回 `BarImpl*` 类型，然后调用用户在 `BarImpl` 类中真正实现的 `process` 方法。
    f. 返回值沿着相反的路径，从 `BarImpl::process` 返回的 C++ `Result` 对象，通过 `into_abi` 转换回 ABI `my_package_Result_t`，最终通过 `from_abi` 转换回调用方的 C++ `Result` 对象。

3. **析构对象**：
    a. 当 `bar` 的所有引用都被销毁时，其引用计数会减少到 0，然后通过 `DataBlockHead` 类型的 `data_ptr` 拿到其 `rtti_ptr`，从中获取到 `BarImpl` 的析构函数并调用。

### 场景二：静态转换（子接口到父接口）

**代码**:
```cpp
using namespace my::package;

IBar bar = ...;
weak::IFoo foo = bar; // 静态转换
```
**调用链**:
1.  该赋值操作触发了 `IBar` 中定义的到 `IFoo` 的转换运算符。
2.  此运算符内部调用了 ABI 层的 `my_package_IBar_1_static` 辅助函数。
3.  `_static` 函数的实现极其高效：它直接对 `IBar` 的虚表指针 `vtbl_ptr` 进行指针运算，加上一个编译时已知的偏移量，直接定位到 `IBar` 虚表中内嵌的 `IFoo` 虚表部分的起始地址。
4.  这个过程完全在编译期确定，无需任何运行时查找，因此称为“静态转换”。

### 场景三：动态转换（任意接口间）

**代码**:
```cpp
using namespace my::package;

IFoo foo = ...;
auto bar = weak::IBar(foo); // 尝试动态转换为 IBar
if (!bar.is_error()) {
    // 转换成功
}
```
**调用链**:
1.  该构造调用了 `weak::IBar` 的 `explicit IBar(::taihe::data_view other)` 构造函数。
2.  此构造函数内部调用了 ABI 层的 `my_package_IBar_dynamic` 辅助函数。
3.  `_dynamic` 函数执行以下运行时操作：
    a. 通过 `foo` 对象的 `data_ptr` 找到 `DataBlockHead`。
    b. 通过 `DataBlockHead` 上的 `rtti_ptr` 找到 `typeinfo` 结构。
    c. 遍历 `typeinfo` 中的 `idmap` 数组。
    d. 将 `idmap` 中每个条目的 `id` 与目标接口的 IID（`my_package_IBar_i`）进行比较。
    e. 如果找到匹配项，则返回该条目对应的 `vtbl_ptr`。
    f. 如果遍历完仍未找到，返回 `NULL`。
4.  C++ 层的构造函数接收到返回的 `vtbl_ptr`。如果为 `NULL`，则 `bar.is_error()` 将返回 `true`，表示转换失败。

## 附录：生成文件的完整内容

以 `my.package` 为例，以下是生成的文件内容，按生成的后端排列。

### `abi-header`

```c
// File: example/generated/include/my.package.Data.abi.0.h
#pragma once
#include "taihe/common.h"
struct my_package_Data_t;

// File: example/generated/include/my.package.Data.abi.1.h
#pragma once
#include "my.package.Data.abi.0.h"
#include "taihe/string.abi.h"
struct my_package_Data_t {
    int32_t a;
    struct TString b;
};

// File: example/generated/include/my.package.Data.abi.2.h
#pragma once
#include "my.package.Data.abi.1.h"

// File: example/generated/include/my.package.Result.abi.0.h
#pragma once
#include "taihe/common.h"
union my_package_Result_union;
struct my_package_Result_t;

// File: example/generated/include/my.package.Result.abi.1.h
#pragma once
#include "my.package.Result.abi.0.h"
#include "taihe/string.abi.h"
union my_package_Result_union {
    int32_t ok;
    struct TString err;
};
struct my_package_Result_t {
    int m_tag;
    union my_package_Result_union m_data;
};

// File: example/generated/include/my.package.Result.abi.2.h
#pragma once
#include "my.package.Result.abi.1.h"

// File: example/generated/include/my.package.IFoo.abi.0.h
#pragma once
#include "taihe/object.abi.h"
struct my_package_IFoo_t;

// File: example/generated/include/my.package.IFoo.abi.1.h
#pragma once
#include "my.package.IFoo.abi.0.h"
struct my_package_IFoo_ftable;
struct my_package_IFoo_vtable {
    struct my_package_IFoo_ftable const* ftbl_ptr_0;
};
TH_EXPORT void const* const my_package_IFoo_i;
struct my_package_IFoo_t {
    struct my_package_IFoo_vtable const* vtbl_ptr;
    struct DataBlockHead* data_ptr;
};
TH_INLINE struct my_package_IFoo_vtable const* my_package_IFoo_dynamic(struct TypeInfo const* rtti_ptr) {
    for (size_t i = 0; i < rtti_ptr->len; i++) {
        if (rtti_ptr->idmap[i].id == my_package_IFoo_i) {
            return (struct my_package_IFoo_vtable const*)rtti_ptr->idmap[i].vtbl_ptr;
        }
    }
    return NULL;
}

// File: example/generated/include/my.package.IFoo.abi.2.h
#pragma once
#include "my.package.IFoo.abi.1.h"
struct my_package_IFoo_ftable {
    void (*init)(struct my_package_IFoo_t tobj);
};
TH_INLINE void my_package_IFoo_init_f(struct my_package_IFoo_t tobj) {
    return tobj.vtbl_ptr->ftbl_ptr_0->init(tobj);
}

// File: example/generated/include/my.package.IBar.abi.0.h
#pragma once
#include "taihe/object.abi.h"
struct my_package_IBar_t;

// File: example/generated/include/my.package.IBar.abi.1.h
#pragma once
#include "my.package.IBar.abi.0.h"
#include "my.package.IFoo.abi.1.h"
struct my_package_IBar_ftable;
struct my_package_IBar_vtable {
    struct my_package_IBar_ftable const* ftbl_ptr_0;
    struct my_package_IFoo_ftable const* ftbl_ptr_1;
};
TH_EXPORT void const* const my_package_IBar_i;
struct my_package_IBar_t {
    struct my_package_IBar_vtable const* vtbl_ptr;
    struct DataBlockHead* data_ptr;
};
TH_INLINE struct my_package_IFoo_vtable const* my_package_IBar_1_static(struct my_package_IBar_vtable const* vtbl_ptr) {
    return vtbl_ptr ? (struct my_package_IFoo_vtable const*)((void* const*)vtbl_ptr + 1) : NULL;
}
TH_INLINE struct my_package_IBar_vtable const* my_package_IBar_dynamic(struct TypeInfo const* rtti_ptr) {
    for (size_t i = 0; i < rtti_ptr->len; i++) {
        if (rtti_ptr->idmap[i].id == my_package_IBar_i) {
            return (struct my_package_IBar_vtable const*)rtti_ptr->idmap[i].vtbl_ptr;
        }
    }
    return NULL;
}

// File: example/generated/include/my.package.IBar.abi.2.h
#pragma once
#include "my.package.IBar.abi.1.h"
#include "my.package.Data.abi.1.h"
#include "my.package.Result.abi.1.h"
#include "my.package.IFoo.abi.2.h"
#include "my.package.Data.abi.2.h"
#include "my.package.Result.abi.2.h"
struct my_package_IBar_ftable {
    struct my_package_Result_t (*process)(struct my_package_IBar_t tobj, struct my_package_Data_t const* data);
};
TH_INLINE struct my_package_Result_t my_package_IBar_process_f(struct my_package_IBar_t tobj, struct my_package_Data_t const* data) {
    return tobj.vtbl_ptr->ftbl_ptr_0->process(tobj, data);
}

// File: example/generated/include/my.package.abi.h
#pragma once
#include "my.package.Data.abi.2.h"
#include "my.package.Result.abi.2.h"
#include "my.package.IFoo.abi.2.h"
#include "my.package.IBar.abi.2.h"
#include "taihe/common.h"
TH_EXPORT struct my_package_Result_t my_package_processWithBar_f(struct my_package_IBar_t bar, struct my_package_Data_t const* data);
```

### `abi-source`

```c
// File: example/generated/src/my.package.abi.c
#include "my.package.IFoo.abi.1.h"
#include "my.package.IBar.abi.1.h"
void const* const my_package_IFoo_i = &my_package_IFoo_i;
void const* const my_package_IBar_i = &my_package_IBar_i;
```

### `cpp-common`

```cpp
// File: example/generated/include/my.package.Data.proj.0.hpp
#pragma once
#include "taihe/common.hpp"
#include "my.package.Data.abi.0.h"
namespace my::package {
struct Data;
}
namespace taihe {
template<>
struct as_abi<::my::package::Data> {
    using type = struct my_package_Data_t;
};
template<>
struct as_abi<::my::package::Data const&> {
    using type = struct my_package_Data_t const*;
};
template<>
struct as_param<::my::package::Data> {
    using type = ::my::package::Data const&;
};
}

// File: example/generated/include/my.package.Data.proj.1.hpp
#pragma once
#include "my.package.Data.proj.0.hpp"
#include "my.package.Data.abi.1.h"
#include "taihe/string.hpp"
namespace my::package {
struct Data {
    int32_t a;
    ::taihe::string b;
};
}
namespace my::package {
inline bool operator==(::my::package::Data const& lhs, ::my::package::Data const& rhs) {
    return true && lhs.a == rhs.a && lhs.b == rhs.b;
}
}
template<> struct ::std::hash<::my::package::Data> {
    size_t operator()(::my::package::Data const& val) const {
        ::std::size_t seed = 0;
        seed ^= ::std::hash<int32_t>()(val.a) + 0x9e3779b9 + (seed << 6) + (seed >> 2);
        seed ^= ::std::hash<::taihe::string>()(val.b) + 0x9e3779b9 + (seed << 6) + (seed >> 2);
        return seed;
    }
};

// File: example/generated/include/my.package.Data.proj.2.hpp
#pragma once
#include "my.package.Data.proj.1.hpp"
#include "my.package.Data.abi.2.h"

// File: example/generated/include/my.package.Result.proj.0.hpp
#pragma once
#include "taihe/common.hpp"
#include "my.package.Result.abi.0.h"
namespace my::package {
struct Result;
}
namespace taihe {
template<>
struct as_abi<::my::package::Result> {
    using type = struct my_package_Result_t;
};
template<>
struct as_abi<::my::package::Result const&> {
    using type = struct my_package_Result_t const*;
};
template<>
struct as_param<::my::package::Result> {
    using type = ::my::package::Result const&;
};
}

// File: example/generated/include/my.package.Result.proj.1.hpp
#pragma once
#include "my.package.Result.proj.0.hpp"
#include "my.package.Result.abi.1.h"
#include "taihe/string.hpp"
namespace my::package {
struct Result {
    public:
    enum class tag_t : int {
        ok,
        err,
    };
    union storage_t {
        storage_t() {}
        ~storage_t() {}
        int32_t ok;
        ::taihe::string err;
    };
    Result(Result const& other) : m_tag(other.m_tag) {
        switch (m_tag) {
        case tag_t::ok: {
            new (&m_data.ok) decltype(m_data.ok)(other.m_data.ok);
            break;
        }
        case tag_t::err: {
            new (&m_data.err) decltype(m_data.err)(other.m_data.err);
            break;
        }
        default: {
            break;
        }
        }
    }
    Result(Result&& other) : m_tag(other.m_tag) {
        switch (m_tag) {
        case tag_t::ok: {
            new (&m_data.ok) decltype(m_data.ok)(::std::move(other.m_data.ok));
            break;
        }
        case tag_t::err: {
            new (&m_data.err) decltype(m_data.err)(::std::move(other.m_data.err));
            break;
        }
        default: {
            break;
        }
        }
    }
    Result& operator=(Result const& other) {
        if (this != &other) {
            ::std::destroy_at(this);
            new (this) Result(other);
        }
        return *this;
    }
    Result& operator=(Result&& other) {
        if (this != &other) {
            ::std::destroy_at(this);
            new (this) Result(::std::move(other));
        }
        return *this;
    }
    ~Result() {
        switch (m_tag) {
        case tag_t::ok: {
            ::std::destroy_at(&m_data.ok);
            break;
        }
        case tag_t::err: {
            ::std::destroy_at(&m_data.err);
            break;
        }
        default: {
            break;
        }
        }
    }
    template<typename... Args>
    Result(::taihe::static_tag_t<tag_t::ok>, Args&&... args) : m_tag(tag_t::ok) {
        new (&m_data.ok) decltype(m_data.ok)(::std::forward<Args>(args)...);
    }
    template<typename... Args>
    Result(::taihe::static_tag_t<tag_t::err>, Args&&... args) : m_tag(tag_t::err) {
        new (&m_data.err) decltype(m_data.err)(::std::forward<Args>(args)...);
    }
    template<tag_t tag, typename... Args>
    static Result make(Args&&... args) {
        return Result(::taihe::static_tag<tag>, ::std::forward<Args>(args)...);
    }
    template<tag_t tag, typename... Args>
    Result const& emplace(Args&&... args) {
        ::std::destroy_at(this);
        new (this) Result(::taihe::static_tag<tag>, ::std::forward<Args>(args)...);
        return *this;
    }
    tag_t get_tag() const {
        return m_tag;
    }
    template<tag_t tag>
    bool holds() const {
        return m_tag == tag;
    }
    template<tag_t tag>
    auto& get_ref() {
        if constexpr (tag == tag_t::ok) {
            return m_data.ok;
        }
        if constexpr (tag == tag_t::err) {
            return m_data.err;
        }
    }
    template<tag_t tag>
    auto* get_ptr() {
        return m_tag == tag ? &get_ref<tag>() : nullptr;
    }
    template<typename Visitor>
    decltype(auto) match_function(Visitor&& visitor) {
        switch (m_tag) {
        case tag_t::ok: {
            return visitor(::taihe::static_tag<tag_t::ok>, m_data.ok);
        }
        case tag_t::err: {
            return visitor(::taihe::static_tag<tag_t::err>, m_data.err);
        }
        }
    }
    template<typename ReturnType, typename Visitor>
    ReturnType match_function(Visitor&& visitor) {
        switch (m_tag) {
        case tag_t::ok: {
            return visitor(::taihe::static_tag<tag_t::ok>, m_data.ok);
        }
        case tag_t::err: {
            return visitor(::taihe::static_tag<tag_t::err>, m_data.err);
        }
        }
    }
    template<tag_t tag>
    auto const& get_ref() const {
        if constexpr (tag == tag_t::ok) {
            return m_data.ok;
        }
        if constexpr (tag == tag_t::err) {
            return m_data.err;
        }
    }
    template<tag_t tag>
    auto const* get_ptr() const {
        return m_tag == tag ? &get_ref<tag>() : nullptr;
    }
    template<typename Visitor>
    decltype(auto) match_function(Visitor&& visitor) const {
        switch (m_tag) {
        case tag_t::ok: {
            return visitor(::taihe::static_tag<tag_t::ok>, m_data.ok);
        }
        case tag_t::err: {
            return visitor(::taihe::static_tag<tag_t::err>, m_data.err);
        }
        }
    }
    template<typename ReturnType, typename Visitor>
    ReturnType match_function(Visitor&& visitor) const {
        switch (m_tag) {
        case tag_t::ok: {
            return visitor(::taihe::static_tag<tag_t::ok>, m_data.ok);
        }
        case tag_t::err: {
            return visitor(::taihe::static_tag<tag_t::err>, m_data.err);
        }
        }
    }
    template<typename... Args>
    static Result make_ok(Args&&... args) {
        return make<tag_t::ok>(::std::forward<Args>(args)...);
    }
    template<typename... Args>
    static Result make_err(Args&&... args) {
        return make<tag_t::err>(::std::forward<Args>(args)...);
    }
    template<typename... Args>
    Result const& emplace_ok(Args&&... args) {
        return emplace<tag_t::ok>(::std::forward<Args>(args)...);
    }
    template<typename... Args>
    Result const& emplace_err(Args&&... args) {
        return emplace<tag_t::err>(::std::forward<Args>(args)...);
    }
    bool holds_ok() const {
        return holds<tag_t::ok>();
    }
    bool holds_err() const {
        return holds<tag_t::err>();
    }
    auto* get_ok_ptr() {
        return get_ptr<tag_t::ok>();
    }
    auto* get_err_ptr() {
        return get_ptr<tag_t::err>();
    }
    auto& get_ok_ref() {
        return get_ref<tag_t::ok>();
    }
    auto& get_err_ref() {
        return get_ref<tag_t::err>();
    }
    template<typename Visitor>
    decltype(auto) match(Visitor&& visitor) {
        switch (m_tag) {
        case tag_t::ok: {
            return visitor.case_ok(m_data.ok);
        }
        case tag_t::err: {
            return visitor.case_err(m_data.err);
        }
        }
    }
    template<typename ReturnType, typename Visitor>
    ReturnType match(Visitor&& visitor) {
        switch (m_tag) {
        case tag_t::ok: {
            return visitor.case_ok(m_data.ok);
        }
        case tag_t::err: {
            return visitor.case_err(m_data.err);
        }
        }
    }
    auto const* get_ok_ptr() const {
        return get_ptr<tag_t::ok>();
    }
    auto const* get_err_ptr() const {
        return get_ptr<tag_t::err>();
    }
    auto const& get_ok_ref() const {
        return get_ref<tag_t::ok>();
    }
    auto const& get_err_ref() const {
        return get_ref<tag_t::err>();
    }
    template<typename Visitor>
    decltype(auto) match(Visitor&& visitor) const {
        switch (m_tag) {
        case tag_t::ok: {
            return visitor.case_ok(m_data.ok);
        }
        case tag_t::err: {
            return visitor.case_err(m_data.err);
        }
        }
    }
    template<typename ReturnType, typename Visitor>
    ReturnType match(Visitor&& visitor) const {
        switch (m_tag) {
        case tag_t::ok: {
            return visitor.case_ok(m_data.ok);
        }
        case tag_t::err: {
            return visitor.case_err(m_data.err);
        }
        }
    }
    private:
    tag_t m_tag;
    storage_t m_data;
};
}
namespace my::package {
inline bool operator==(::my::package::Result const& lhs, ::my::package::Result const& rhs) {
    return false || (lhs.holds_ok() && rhs.holds_ok() && lhs.get_ok_ref() == rhs.get_ok_ref()) || (lhs.holds_err() && rhs.holds_err() && lhs.get_err_ref() == rhs.get_err_ref());
}
}
template<> struct ::std::hash<::my::package::Result> {
    size_t operator()(::my::package::Result const& val) const {
        switch (val.get_tag()) {
        case ::my::package::Result::tag_t::ok: {
            ::std::size_t seed = ::std::hash<int>()(static_cast<int>(::my::package::Result::tag_t::ok));
            return seed ^ (0x9e3779b9 + (seed << 6) + (seed >> 2) + ::std::hash<int32_t>()(val.get_ok_ref()));
        }
        case ::my::package::Result::tag_t::err: {
            ::std::size_t seed = ::std::hash<int>()(static_cast<int>(::my::package::Result::tag_t::err));
            return seed ^ (0x9e3779b9 + (seed << 6) + (seed >> 2) + ::std::hash<::taihe::string>()(val.get_err_ref()));
        }
        }
    }
};

// File: example/generated/include/my.package.Result.proj.2.hpp
#pragma once
#include "my.package.Result.proj.1.hpp"
#include "my.package.Result.abi.2.h"

// File: example/generated/include/my.package.IFoo.proj.0.hpp
#pragma once
#include "taihe/object.hpp"
#include "my.package.IFoo.abi.0.h"
namespace my::package::weak {
struct IFoo;
}
namespace my::package {
struct IFoo;
}
namespace taihe {
template<>
struct as_abi<::my::package::IFoo> {
    using type = struct my_package_IFoo_t;
};
template<>
struct as_abi<::my::package::weak::IFoo> {
    using type = struct my_package_IFoo_t;
};
template<>
struct as_param<::my::package::IFoo> {
    using type = ::my::package::weak::IFoo;
};
}

// File: example/generated/include/my.package.IFoo.proj.1.hpp
#pragma once
#include "my.package.IFoo.proj.0.hpp"
#include "my.package.IFoo.abi.1.h"
namespace my::package::weak {
struct IFoo {
    static constexpr bool is_holder = false;
    struct my_package_IFoo_t m_handle;
    explicit IFoo(struct my_package_IFoo_t handle) : m_handle(handle) {}
    operator ::taihe::data_view() const& {
        return ::taihe::data_view(this->m_handle.data_ptr);
    }
    operator ::taihe::data_holder() const& {
        return ::taihe::data_holder(tobj_dup(this->m_handle.data_ptr));
    }
    explicit IFoo(::taihe::data_view other) : IFoo({
        my_package_IFoo_dynamic(other.data_ptr->rtti_ptr),
        other.data_ptr,
    }) {}
    struct virtual_type;
    template<typename Impl>
    struct methods_impl;
    template<typename Impl>
    static const my_package_IFoo_ftable ftbl_impl;
    template<typename Impl>
    static constexpr my_package_IFoo_vtable vtbl_impl = {
        .ftbl_ptr_0 = &::my::package::weak::IFoo::template ftbl_impl<Impl>,
    };
    template<typename Impl>
    static constexpr struct IdMapItem idmap_impl[1] = {
        {&my_package_IFoo_i, &vtbl_impl<Impl>.ftbl_ptr_0},
    };
    using vtable_type = my_package_IFoo_vtable;
    using view_type = ::my::package::weak::IFoo;
    using holder_type = ::my::package::IFoo;
    using abi_type = my_package_IFoo_t;
    bool is_error() const& {
        return m_handle.vtbl_ptr == nullptr;
    }
    virtual_type const& operator*() const& {
        return *reinterpret_cast<virtual_type const*>(&m_handle);
    }
    virtual_type const* operator->() const& {
        return reinterpret_cast<virtual_type const*>(&m_handle);
    }
};
}
namespace my::package {
struct IFoo : public ::my::package::weak::IFoo {
    static constexpr bool is_holder = true;
    explicit IFoo(struct my_package_IFoo_t handle) : ::my::package::weak::IFoo(handle) {}
    IFoo& operator=(::my::package::IFoo other) {
        ::std::swap(this->m_handle, other.m_handle);
        return *this;
    }
    ~IFoo() {
        tobj_drop(this->m_handle.data_ptr);
    }
    operator ::taihe::data_view() const& {
        return ::taihe::data_view(this->m_handle.data_ptr);
    }
    operator ::taihe::data_holder() const& {
        return ::taihe::data_holder(tobj_dup(this->m_handle.data_ptr));
    }
    operator ::taihe::data_holder() && {
        return ::taihe::data_holder(std::exchange(this->m_handle.data_ptr, nullptr));
    }
    explicit IFoo(::taihe::data_holder other) : IFoo({
        my_package_IFoo_dynamic(other.data_ptr->rtti_ptr),
        std::exchange(other.data_ptr, nullptr),
    }) {}
    IFoo(::my::package::weak::IFoo const& other) : IFoo({
        other.m_handle.vtbl_ptr,
        tobj_dup(other.m_handle.data_ptr),
    }) {}
    IFoo(::my::package::IFoo const& other) : IFoo({
        other.m_handle.vtbl_ptr,
        tobj_dup(other.m_handle.data_ptr),
    }) {}
    IFoo(::my::package::IFoo&& other) : IFoo({
        other.m_handle.vtbl_ptr,
        std::exchange(other.m_handle.data_ptr, nullptr),
    }) {}
};
}
namespace my::package::weak {
inline bool operator==(::my::package::weak::IFoo lhs, ::my::package::weak::IFoo rhs) {
    return ::taihe::data_view(lhs) == ::taihe::data_view(rhs);
}
}
template<> struct ::std::hash<::my::package::IFoo> {
    size_t operator()(::my::package::weak::IFoo val) const {
        return ::std::hash<::taihe::data_holder>()(val);
    }
};

// File: example/generated/include/my.package.IFoo.proj.2.hpp
#pragma once
#include "my.package.IFoo.proj.1.hpp"
#include "my.package.IFoo.abi.2.h"
struct ::my::package::weak::IFoo::virtual_type {
    void init() const& {
        return my_package_IFoo_init_f(*reinterpret_cast<my_package_IFoo_t const*>(this));
    }
};
template<typename Impl>
struct ::my::package::weak::IFoo::methods_impl {
    static void init(struct my_package_IFoo_t tobj) {
        return ::taihe::cast_data_ptr<Impl>(tobj.data_ptr)->init();
    }
};
template<typename Impl>
constexpr my_package_IFoo_ftable my::package::weak::IFoo::ftbl_impl = {
    .init = &methods_impl<Impl>::init,
};

// File: example/generated/include/my.package.IBar.proj.0.hpp
#pragma once
#include "taihe/object.hpp"
#include "my.package.IBar.abi.0.h"
namespace my::package::weak {
struct IBar;
}
namespace my::package {
struct IBar;
}
namespace taihe {
template<>
struct as_abi<::my::package::IBar> {
    using type = struct my_package_IBar_t;
};
template<>
struct as_abi<::my::package::weak::IBar> {
    using type = struct my_package_IBar_t;
};
template<>
struct as_param<::my::package::IBar> {
    using type = ::my::package::weak::IBar;
};
}

// File: example/generated/include/my.package.IBar.proj.1.hpp
#pragma once
#include "my.package.IBar.proj.0.hpp"
#include "my.package.IBar.abi.1.h"
#include "my.package.IFoo.proj.1.hpp"
namespace my::package::weak {
struct IBar {
    static constexpr bool is_holder = false;
    struct my_package_IBar_t m_handle;
    explicit IBar(struct my_package_IBar_t handle) : m_handle(handle) {}
    operator ::taihe::data_view() const& {
        return ::taihe::data_view(this->m_handle.data_ptr);
    }
    operator ::taihe::data_holder() const& {
        return ::taihe::data_holder(tobj_dup(this->m_handle.data_ptr));
    }
    explicit IBar(::taihe::data_view other) : IBar({
        my_package_IBar_dynamic(other.data_ptr->rtti_ptr),
        other.data_ptr,
    }) {}
    operator ::my::package::weak::IFoo() const& {
        return ::my::package::weak::IFoo({
            my_package_IBar_1_static(this->m_handle.vtbl_ptr),
            this->m_handle.data_ptr,
        });
    }
    operator ::my::package::IFoo() const& {
        return ::my::package::IFoo({
            my_package_IBar_1_static(this->m_handle.vtbl_ptr),
            tobj_dup(this->m_handle.data_ptr),
        });
    }
    struct virtual_type;
    template<typename Impl>
    struct methods_impl;
    template<typename Impl>
    static const my_package_IBar_ftable ftbl_impl;
    template<typename Impl>
    static constexpr my_package_IBar_vtable vtbl_impl = {
        .ftbl_ptr_0 = &::my::package::weak::IBar::template ftbl_impl<Impl>,
        .ftbl_ptr_1 = &::my::package::weak::IFoo::template ftbl_impl<Impl>,
    };
    template<typename Impl>
    static constexpr struct IdMapItem idmap_impl[2] = {
        {&my_package_IBar_i, &vtbl_impl<Impl>.ftbl_ptr_0},
        {&my_package_IFoo_i, &vtbl_impl<Impl>.ftbl_ptr_1},
    };
    using vtable_type = my_package_IBar_vtable;
    using view_type = ::my::package::weak::IBar;
    using holder_type = ::my::package::IBar;
    using abi_type = my_package_IBar_t;
    bool is_error() const& {
        return m_handle.vtbl_ptr == nullptr;
    }
    virtual_type const& operator*() const& {
        return *reinterpret_cast<virtual_type const*>(&m_handle);
    }
    virtual_type const* operator->() const& {
        return reinterpret_cast<virtual_type const*>(&m_handle);
    }
};
}
namespace my::package {
struct IBar : public ::my::package::weak::IBar {
    static constexpr bool is_holder = true;
    explicit IBar(struct my_package_IBar_t handle) : ::my::package::weak::IBar(handle) {}
    IBar& operator=(::my::package::IBar other) {
        ::std::swap(this->m_handle, other.m_handle);
        return *this;
    }
    ~IBar() {
        tobj_drop(this->m_handle.data_ptr);
    }
    operator ::taihe::data_view() const& {
        return ::taihe::data_view(this->m_handle.data_ptr);
    }
    operator ::taihe::data_holder() const& {
        return ::taihe::data_holder(tobj_dup(this->m_handle.data_ptr));
    }
    operator ::taihe::data_holder() && {
        return ::taihe::data_holder(std::exchange(this->m_handle.data_ptr, nullptr));
    }
    explicit IBar(::taihe::data_holder other) : IBar({
        my_package_IBar_dynamic(other.data_ptr->rtti_ptr),
        std::exchange(other.data_ptr, nullptr),
    }) {}
    IBar(::my::package::weak::IBar const& other) : IBar({
        other.m_handle.vtbl_ptr,
        tobj_dup(other.m_handle.data_ptr),
    }) {}
    IBar(::my::package::IBar const& other) : IBar({
        other.m_handle.vtbl_ptr,
        tobj_dup(other.m_handle.data_ptr),
    }) {}
    IBar(::my::package::IBar&& other) : IBar({
        other.m_handle.vtbl_ptr,
        std::exchange(other.m_handle.data_ptr, nullptr),
    }) {}
    operator ::my::package::weak::IFoo() const& {
        return ::my::package::weak::IFoo({
            my_package_IBar_1_static(this->m_handle.vtbl_ptr),
            this->m_handle.data_ptr,
        });
    }
    operator ::my::package::IFoo() const& {
        return ::my::package::IFoo({
            my_package_IBar_1_static(this->m_handle.vtbl_ptr),
            tobj_dup(this->m_handle.data_ptr),
        });
    }
    operator ::my::package::IFoo() && {
        return ::my::package::IFoo({
            my_package_IBar_1_static(this->m_handle.vtbl_ptr),
            std::exchange(this->m_handle.data_ptr, nullptr),
        });
    }
};
}
namespace my::package::weak {
inline bool operator==(::my::package::weak::IBar lhs, ::my::package::weak::IBar rhs) {
    return ::taihe::data_view(lhs) == ::taihe::data_view(rhs);
}
}
template<> struct ::std::hash<::my::package::IBar> {
    size_t operator()(::my::package::weak::IBar val) const {
        return ::std::hash<::taihe::data_holder>()(val);
    }
};

// File: example/generated/include/my.package.IBar.proj.2.hpp
#pragma once
#include "my.package.IBar.proj.1.hpp"
#include "my.package.IBar.abi.2.h"
#include "my.package.Data.proj.1.hpp"
#include "my.package.Result.proj.1.hpp"
#include "my.package.IFoo.proj.2.hpp"
#include "my.package.Data.proj.2.hpp"
#include "my.package.Result.proj.2.hpp"
struct ::my::package::weak::IBar::virtual_type {
    ::my::package::Result process(::my::package::Data const& data) const& {
        return ::taihe::from_abi<::my::package::Result>(my_package_IBar_process_f(*reinterpret_cast<my_package_IBar_t const*>(this), ::taihe::into_abi<::my::package::Data const&>(data)));
    }
};
template<typename Impl>
struct ::my::package::weak::IBar::methods_impl {
    static struct my_package_Result_t process(struct my_package_IBar_t tobj, struct my_package_Data_t const* data) {
        return ::taihe::into_abi<::my::package::Result>(::taihe::cast_data_ptr<Impl>(tobj.data_ptr)->process(::taihe::from_abi<::my::package::Data const&>(data)));
    }
};
template<typename Impl>
constexpr my_package_IBar_ftable my::package::weak::IBar::ftbl_impl = {
    .process = &methods_impl<Impl>::process,
};

// File: example/generated/include/my.package.proj.hpp
#pragma once
#include "my.package.Data.proj.2.hpp"
#include "my.package.Result.proj.2.hpp"
#include "my.package.IFoo.proj.2.hpp"
#include "my.package.IBar.proj.2.hpp"
```

### `cpp-user`

```cpp
#pragma once
#include "my.package.proj.hpp"
#include "taihe/common.hpp"
#include "my.package.abi.h"
#include "my.package.IBar.proj.2.hpp"
#include "my.package.Data.proj.2.hpp"
#include "my.package.Result.proj.2.hpp"
namespace my::package {
inline ::my::package::Result processWithBar(::my::package::weak::IBar bar, ::my::package::Data const& data) {
    return ::taihe::from_abi<::my::package::Result>(my_package_processWithBar_f(::taihe::into_abi<::my::package::weak::IBar>(bar), ::taihe::into_abi<::my::package::Data const&>(data)));
}
}
```

### `cpp-author`

```cpp
// File: example/generated/include/my.package.impl.hpp
#pragma once
#include "taihe/common.hpp"
#include "my.package.abi.h"
#include "my.package.IBar.proj.2.hpp"
#include "my.package.Data.proj.2.hpp"
#include "my.package.Result.proj.2.hpp"
#define TH_EXPORT_CPP_API_processWithBar(CPP_FUNC_IMPL) \
    struct my_package_Result_t my_package_processWithBar_f(struct my_package_IBar_t bar, struct my_package_Data_t const* data) { \
        return ::taihe::into_abi<::my::package::Result>(CPP_FUNC_IMPL(::taihe::from_abi<::my::package::weak::IBar>(bar), ::taihe::from_abi<::my::package::Data const&>(data))); \
    }
```

### `cpp-author-template`

```cpp
// File: example/generated/temp/my.package.impl.cpp
#include "my.package.proj.hpp"
#include "my.package.impl.hpp"
#include "taihe/runtime.hpp"
#include "stdexcept"

namespace {
class IFooImpl {
    public:
    IFooImpl() {
        // Don't forget to implement the constructor.
    }

    void init() {
        TH_THROW(std::runtime_error, "init not implemented");
    }
};

class IBarImpl {
    public:
    IBarImpl() {
        // Don't forget to implement the constructor.
    }

    ::my::package::Result process(::my::package::Data const& data) {
        TH_THROW(std::runtime_error, "process not implemented");
    }

    void init() {
        TH_THROW(std::runtime_error, "init not implemented");
    }
};

::my::package::Result processWithBar(::my::package::weak::IBar bar, ::my::package::Data const& data) {
    TH_THROW(std::runtime_error, "processWithBar not implemented");
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_processWithBar(processWithBar);
// NOLINTEND
```
