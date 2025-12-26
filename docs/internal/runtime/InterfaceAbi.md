# Taihe 面向对象/接口系统设计和实现文档

## 1. 概述

Taihe 面向对象系统的设计目标是提供一种完全基于**接口**的编程模型，允许接口的多重继承，菱形继承，静态转换和动态转换，并且支持接口对象的引用计数管理。为了实现这些目标，Taihe 定义了一套应用程序二进制接口（ABI），使得不同编译器生成的代码能够互操作。

## 2. Taihe ABI 设计

### 2.1 IDL 接口定义示例

以一个菱形继承的场景为例，假设我们有一个接口 `IFancyObj`，它继承了两个接口 `IColor` 和 `IShape`，而这两个接口又都继承自 `IBase`。我们可以定义如下的接口：

```rust
interface IBase {
  getState(): bool;
  setState(s: bool): void;
}

interface IColor: IBase {
  getColor(): String;
  setColor(c: String): void;
}

interface IShape: IBase {
  getShape(): String;
  setShape(s: String): void;
}

interface IFancyObj: IColor, IShape {
  sparkle(): void;
}
```

### 2.2 Taihe 接口对象内存布局

#### 2.2.1 胖指针结构

一个 Taihe 接口对象由两个指针构成，它们分别指向**虚表**和**数据块**。

```c
struct IFancyObj {
  struct IFancyObj_vtable const* vtbl_ptr;  // 指向虚表
  struct DataBlockHead* data_ptr;           // 指向数据块头
};
```

#### 2.2.2 虚表

对于在 IDL 中定义的每个接口，其**虚表**结构体中的第一项应是指向该接口的**函数表**结构体的指针，接下来则应按顺序排入该接口*直接*继承的所有父接口的虚表中的*完整内存排布*。

```c
struct IBase_vtable {
  struct IBase_ftable const* ftbl_ptr;  // 指向 IBase 的函数表
};

struct IColor_vtable {
  struct IColor_ftable const* ftbl_ptr;  // 指向 IColor 的函数表
  struct IBase_vtable IBase_vtbl;        // IBase 的虚表
};

struct IShape_vtable {
  struct IShape_ftable const* ftbl_ptr;  // 指向 IShape 的函数表
  struct IBase_vtable IBase_vtbl;        // IBase 的虚表
};

struct IFancyObj_vtable {
  struct IFancyObj_ftable const* ftbl_ptr;  // 指向 IFancyObj 的函数表
  struct IColor_vtable IColor_vtbl;         // IColor 的虚表
  struct IShape_vtable IShape_vtbl;         // IShape 的虚表
}
```

实际生成的 ABI 层代码中，虚表的嵌套结构会被*扁平化展开*，例如上述的 `IFancyObj_vtable` 实际上会被展开为如下结构：

```c
struct IFancyObj_vtable {
  struct IFancyObj_ftable const* ftbl_ptr_0;  // 指向 IFancyObj 的函数表
  struct IColor_ftable const* ftbl_ptr_1;     // 指向 IColor 的函数表
  struct IBase_ftable const* ftbl_ptr_2;      // 指向 IBase 的函数表
  struct IShape_ftable const* ftbl_ptr_3;     // 指向 IShape 的函数表
  struct IBase_ftable const* ftbl_ptr_4;      // 指向 IBase 的函数表
};
```

注意到在 `IFancyObj_vtable` 中，有两个 `IBase_ftable` 的指针。它们实际指向的是同一个 `IBase` 接口的**函数表**，但为了使得一个 `IFancyObj` 对象无论被静态转换成 `IColor` 还是 `IShape` 后都能正确地通过确定的虚表偏移量被转换为 `IBase`，这种重复是必要的。

#### 2.2.3 函数表

每个 Taihe 接口的**函数表**内部则存有这个接口*自己的*所有方法的指针：

```c
struct IBase_ftable {
    bool (*getState)(struct IBase self);
    void (*setState)(struct IBase self, bool s);
};

struct IColor_ftable {
    TString (*getColor)(struct IColor self);
    void (*setColor)(struct IColor self, TString c);
};

struct IShape_ftable {
    TString (*getShape)(struct IShape self);
    void (*setShape)(struct IShape self, TString s);
};

struct IFancyObj_ftable {
    void (*sparkle)(struct IFancyObj self);
};
```

#### 2.2.4 数据块

Taihe 接口对象的**数据块**则由**数据头**和**实际对象内存**两部分构成，其中**数据头**存储了对象的**运行时类型信息**（RTTI）和**引用计数**等元数据。

```c
struct DataBlock {
  struct DataBlockHead head;        // 数据块头
  /* ... */                         // 实际对象内存，包含用户具体实现类里的数据
};

struct DataBlockHead {
  struct TypeInfo const *rtti_ptr;  // 指向运行时类型信息
  TRefCount m_count;                // 引用计数
};
```

#### 2.2.5 运行时类型信息

在**运行时类型信息**中，会包含对象的版本信息，销毁函数、哈希函数及比较函数等通用函数的指针，还有**动态转换表**及其长度。

```c
typedef void free_func_t(struct DataBlockHead *);
typedef size_t hash_func_t(struct DataBlockHead *);
typedef bool same_func_t(struct DataBlockHead *, struct DataBlockHead *);

struct TypeInfo {
  uint64_t version;
  free_func_t *free_fptr;
  hash_func_t *hash_fptr;
  same_func_t *same_fptr;
  uint64_t len;
  struct IdMapItem idmap[];
};
```

其中**动态转换表**由若干**动态转换表项**构成，每个项包含一个**接口 ID** 和指向该接口虚表的指针。

```c
struct IdMapItem {
  void const *id;
  void const *vtbl_ptr;
};
```

#### 2.2.6 接口 ID

**接口 ID** 是一个全局唯一的标识符，在运行时对 Taihe 接口对象进行动态转换时会根据此标识判断该对象是否实现了特定接口。每个在 Taihe IDL 中声明的接口在编译时都会分配一个唯一的 ID。

```c
void const *IBase_iid = ...;
void const *IColor_iid = ...;
void const *IShape_iid = ...;
void const *IFancyObj_iid = ...;
```

### 2.3 方法

#### 2.3.1 静态转换

由于所有的接口继承关系都是已知的，因此可以在编译时直接计算出从一个接口虚表到另一个接口虚表的偏移量。因此静态转换函数的实现就是通过给虚表指针加上固定的偏移量来实现的。

需要注意的时，有些情况下，一个接口可能通过不同路径重复继承了同一个接口。在这种情况下，无论增加该祖先在哪一条路径所对应的偏移量，结果都是正确的，不过通常我们会选择第一条路径。例如，在上面的例子中，`IFancyObj` 通过 `IColor` 和 `IShape` 两条路径都继承了 `IBase`，因此无论是在 `IFancyObj` 对应虚表指针的基础上增加 2 个还是 4 个指针的偏移量，都能正确得到 `IBase` 的虚表指针，但实际实现中我们会选择增加 2 个指针的偏移量。

以下是 `IFancyObj` 接口和它的父接口的静态转换函数示例：

```cpp
struct IBase_vtable const* static_cast_from_IFancyObj_to_IColor(struct IFancyObj_vtable const* vtbl_ptr) {
  if (vtbl_ptr == NULL) {
    return NULL;
  }
  return (struct IBase_vtable const*)((void* const*)vtbl_ptr + 1);
}

struct IBase_vtable const* static_cast_from_IFancyObj_to_IBase(struct IFancyObj_vtable const* vtbl_ptr) {
  if (vtbl_ptr == NULL) {
    return NULL;
  }
  return (struct IBase_vtable const*)((void* const*)vtbl_ptr + 2);
}

struct IShape_vtable const* static_cast_from_IFancyObj_to_IShape(struct IFancyObj_vtable const* vtbl_ptr) {
  if (vtbl_ptr == NULL) {
    return NULL;
  }
  return (struct IShape_vtable const*)((void* const*)vtbl_ptr + 3);
}
```

要对对象进行静态转换时：

```cpp
struct IFancyObj fancy = ...;
struct IBase base = {
  .vtbl_ptr = static_cast_from_IFancyObj_to_IBase(fancy.vtbl_ptr),
  .data_ptr = fancy.data_ptr,
};
```

#### 2.3.2 动态转换

每个对象的数据块头部都有指向其具体类型运行时信息的指针。其中存有该类型的动态转换表。动态转换表是从接口 ID 到相应虚表的映射，用于在运行时查询对象实现的所有接口，从而实现运行时的向下转换。

以下是代码样例，展示了如何从一个不知道实现了哪些接口的对象的运行时类型信息中动态判断其是否实现了 `IFancyObj` 接口并取得对应的虚表指针：

```cpp
struct IFancyObj_vtable const* dynamic_cast_to_IFancyObj(struct TypeInfo const* rtti_ptr) {
  for (size_t i = 0; i < rtti_ptr->len; i++) {
    if (rtti_ptr->idmap[i].id == IFancyObj_iid) {
      return (struct IFancyObj_vtable const*)rtti_ptr->idmap[i].vtbl_ptr;
    }
  }
  return NULL;
}
```

如果要将一个对象转换为 `IFancyObj`，就可以这样做：

```cpp
struct IBase base = ...;
struct IFancyObj fancy = {
  .vtbl_ptr = dynamic_cast_to_IFancyObj(base.data_ptr->rtti_ptr),
  .data_ptr = base.data_ptr,
};
```

#### 2.3.3 函数调用

函数调用通过虚表中的函数指针实现。调用时，首先获取对象的虚表指针，然后根据接口的函数表指针调用相应的方法。

```cpp
void call_IFancyObj_sparkle(struct IFancyObj self) {
  self->vtbl_ptr->ftbl_ptr_0->sparkle(self);
}
```

#### 2.3.4 对象的构造、拷贝和销毁

以下代码截取自 `runtime/taihe/src/object.cpp`，展示了对象的构造、拷贝和销毁过程：

```cpp
void tobj_init(struct DataBlockHead *data_ptr, struct TypeInfo const *rtti_ptr) {
  data_ptr->rtti_ptr = rtti_ptr;
  tref_init(&data_ptr->m_count, 1);
}

struct DataBlockHead *tobj_dup(struct DataBlockHead *data_ptr) {
  if (!data_ptr) {
    return nullptr;
  }
  tref_inc(&data_ptr->m_count);
  return data_ptr;
}

void tobj_drop(struct DataBlockHead *data_ptr) {
  if (!data_ptr) {
    return;
  }
  if (tref_dec(&data_ptr->m_count)) {
    data_ptr->rtti_ptr->free_fptr(data_ptr);
  }
}
```

#### 2.3.5 对象的哈希和比较

对象的哈希和比较通过 `TypeInfo` 中的 `hash_fptr` 和 `same_fptr` 函数指针实现。这些函数指针在对象的运行时类型信息中定义，允许在运行时对对象进行哈希和比较操作。

```cpp
size_t tobj_hash(struct DataBlockHead *data_ptr) {
  return data_ptr->rtti_ptr->hash_fptr(data_ptr);
}

bool tobj_same(struct DataBlockHead *left_ptr, struct DataBlockHead *right_ptr) {
  return left_ptr->rtti_ptr->same_fptr(left_ptr, right_ptr);
}
```

## 3. C++ 层设计和实现

### 3.1 核心设计思想

Taihe IDL 的 C++ 层旨在为开发者提供一种现代化、易于使用且高性能的方式来与 Taihe ABI（应用程序二进制接口）进行交互。其核心设计思想可以概括为以下几点：

1. **零成本抽象**：C++ 层的封装（如对象包装器、方法调用）在编译后应尽可能地减少性能开销。用户在 C++ 中调用一个接口方法，其最终的执行路径应与直接操作 C ABI 的函数指针调用几乎一致。

2. **类型安全与现代 C++ 语法**：将底层的 C 风格 ABI (struct*, void*) 包装成类型安全的 C++ 类。提供 `operator->`、隐式转换等语法糖，使得与 Taihe 对象的交互体验尽可能接近原生的 C++ 对象。

3. **所有权与生命周期管理自动化**：通过类似智能指针的 RAII 机制自动管理对象的引用计数。这极大地简化了开发者的心智负担，避免了手动调用 `tobj_dup` 和 `tobj_drop` 带来的内存泄漏或重复释放问题。并提供 Holder（有引用计数的持有者）和 Borrow（无引用计数的借用者）两种语义，分别对应拥有对象所有权和仅借用对象的场景。

4. **编译时生成与类型擦除**：利用 C++ 模板元编程的强大能力，在编译期为用户的具体实现类 (Impl Class) 自动生成所有必要的 ABI 结构，包括虚表 (VTable) 和运行时类型信息 (RTTI)。这避免了在运行时进行复杂的结构构造，并能提前进行大量的类型检查。无论用户在 C++ 中实现的具体业务逻辑类 (Impl Class) 是什么，一旦它被包装成一个 Taihe 接口对象，其具体的类型信息就会被“擦除”，统一表示为 ABI 定义的 `vtbl_ptr` + `data_ptr` 结构。所有操作都通过虚表和运行时类型信息进行动态分发。

### 3.2 总体架构

整个 C++ 层可以看作一个两层结构：

1. **泛型引擎 (`runtime/object.hpp`)**: 提供了与具体接口无关的、通用的对象创建、生命周期管理和类型转换的模板工具。其中关键抽象包括**实现类容器** `taihe::impl_holder` 和 `taihe::impl_view`，用于表示一个未被类型擦除的、实现了某些特定 Taihe 接口的某个具体实现类的对象。以及**完全类型擦除句柄** `taihe::data_holder` 和 `taihe::data_view`，它们代表一个类型未知的 Taihe 对象，是进行动态类型转换的枢纽。任何 Taihe 接口对象都可以隐式转换为这两种类型。

2. **接口包装器 (`proj.*.hpp`)**: 这些是 IDL 工具根据用户定义的 .idl 文件自动生成的文件。它们为每个 IDL 接口（如 `IBase`, `IFancyObj`）提供了具体的 C++ 包装类如 `object::IBase`（持有者）, `object::weak::IBase`（借用者）等，并包含了用于构建 VTable 和 RTTI 的关键 `constexpr` 模板元数据。

当开发者希望将一个自己的 C++ 类（我们称之为 Impl）包装成 Taihe 接口对象时，实际上是 `object.hpp` 中的泛型引擎使用了 `proj.*.hpp` 中为该接口准备好的“蓝图”和“零件”，在编译时根据这个特定的 Impl 类特化相应模板并组装出完整的 ABI 结构。

### 3.3 使用

#### 3.3.1 对象创建

创建 Taihe 接口对象的 C++ 工具函数是 `taihe::make_holder<Impl, InterfaceA, InterfaceB, ...>(args...)`。它接受一个用户定义的具体实现类 `Impl`，以及该实现类所实现的 Taihe 接口列表 `InterfaceA, InterfaceB, ...`，并传递给 `Impl` 的构造函数参数 `Impl(args...)`。

例如，假设 `MyObject` 实现了 `IColor` 和 `IShape` 两个接口中的所有方法，那么我们可以这样创建一个 Taihe 接口对象：

```cpp
auto obj = taihe::make_holder<MyObject, IColor, IShape>(constructor_args...);
```

这个调用的过程如下：

1. `make_holder<MyObject, IColor, IShape>` 内部调用了 `impl_holder<MyObject, IColor, IShape>::make(args...)`：

    ```c++
    template<typename Impl, typename... InterfaceTypes, typename... Args>
    inline auto make_holder(Args &&...args) {
      return impl_holder<Impl, InterfaceTypes...>::make(std::forward<Args>(args)...);
    }
    ```

2. `impl_holder<Impl, InterfaceTypes...>` 是一个表示持有者类型的模板类，并继承自相应的借用类型 `impl_view<Impl, InterfaceTypes...>`，该模板类可以在编译器针对具体的 `Impl` 类和接口列表构造相应的的 ABI 结构。其内涵是表示一个实现了 `InterfaceTypes...` 接口的 `Impl` 对象的智能指针。

    ```c++
    template<typename... Args>
    static impl_holder make(Args &&...args) {
      DataBlockHead *data_ptr = make_data_ptr<Impl>(
            reinterpret_cast<TypeInfo const *>(&impl_view<Impl, InterfaceTypes...>::rtti),
            std::forward<Args>(args)...);
      return impl_holder(data_ptr);
    }
    ```

3. 先看这里的 `make_data_ptr<Impl>(...)`，它是一个非成员函数，传入了 `Impl` 类的运行时类型信息 `rtti_ptr`，以及 `Impl` 的构造函数参数。`make_data_ptr` 函数会在堆上 `new` 一个 `data_block<Impl>` 对象，将其指针转换为 `DataBlockHead*` 返回：

    ```c++
    template<typename Impl, typename... Args>
    inline DataBlockHead *make_data_ptr(TypeInfo const *rtti_ptr, Args &&...args) {
      return new data_block<Impl>(rtti_ptr, std::forward<Args>(args)...);
    }
    ```

4. 其中的 `data_block<Impl>` 结构体继承自 `DataBlockHead`，并包含了 `Impl` 类的实际内存：

    ```c++
    template<typename Impl>
    struct data_block : DataBlockHead {
      Impl impl;

      template<typename... Args>
      data_block(TypeInfo const *rtti_ptr, Args &&...args) : impl(std::forward<Args>(args)...) {
        tobj_init(this, rtti_ptr);
      }
    };
    ```

5. 注意到步骤 2 中使用了 `impl_view<Impl, InterfaceTypes...>::rtti`，这是一个 `constexpr` 静态成员变量，定义在 `impl_view` 模板类内部。它在编译期根据 `Impl` 类和接口列表 `InterfaceTypes...` 生成了完整的运行时类型信息：

    ```c++
    struct typeinfo_t {
      uint64_t version;
      free_func_t *free_fptr;
      hash_func_t *hash_fptr;
      same_func_t *same_fptr;
      uint64_t len;
      struct IdMapItem idmap[((sizeof(InterfaceTypes::template idmap_impl<Impl>) / sizeof(IdMapItem)) + ...)];
    };
    static constexpr typeinfo_t rtti = [] {
      struct typeinfo_t info = {
        .version = 0,
        .free_fptr = &free_data_ptr<Impl>,
        .hash_fptr = &hash_data_ptr<Impl>,
        .same_fptr = &same_data_ptr<Impl>,
      };
      // 使用折叠表达式展开所有接口的 idmap_impl
      info.len = 0;
      (
        [&] {
          using InterfaceType = InterfaceTypes;
          for (std::size_t j = 0; j < sizeof(InterfaceType::template idmap_impl<Impl>) / sizeof(IdMapItem); info.len++, j++) {
            info.idmap[info.len] = InterfaceType::template idmap_impl<Impl>[j];
          }
        }(),
      ...);
      return info;
    }();
    ```

6. `free_data_ptr<Impl>`, `hash_data_ptr<Impl>` 和 `same_data_ptr<Impl>` 是几个非成员模板函数，用于实现对象的销毁、哈希和比较，这里以 `free_data_ptr<Impl>` 为例，它基本可以看作 `make_data_ptr<Impl>` 的逆操作：

    ```c++
    template<typename Impl>
    inline void free_data_ptr(struct DataBlockHead *data_ptr) {
      delete static_cast<data_block<Impl> *>(data_ptr);
    }
    ```

7. 其中的 `idmap_impl<Impl>` 是每个接口类（如 `IColor`, `IShape`）中定义的一个编译器静态模板成员变量，定义在 `*.proj.1.hpp` 中。它包含了 `Impl` 类关于该接口及其所有父接口的动态转换表项，例如 `IColor` 的 `idmap_impl` 定义如下：

    ```c++
    template<typename Impl>
    static constexpr struct IdMapItem idmap_impl[2] = {
      {&object_IColor_i, &vtbl_impl<Impl>.ftbl_ptr_0},
      {&object_IBase_i, &vtbl_impl<Impl>.ftbl_ptr_1},
    };
    ```

8. 上面用到的 `vtbl_impl<Impl>` 同样是定义在接口类中的一个编译期静态模板成员变量。它是 `Impl` 类对于该接口的完整虚表结构体：

    ```c++
    template<typename Impl>
    static constexpr object_IColor_vtable vtbl_impl = {
      .ftbl_ptr_0 = &object::weak::IColor::template ftbl_impl<Impl>,
      .ftbl_ptr_1 = &object::weak::IBase::template ftbl_impl<Impl>,
    };
    ```

9. `ftbl_impl<Impl>` 也是接口类的一个编译期静态模板成员变量，它是 `Impl` 类对于该接口的函数表结构体实现，其中的每个函数指针都指向 `methods_impl<Impl>` 结构体中的静态方法，这些方法是对 `Impl` 类中对应方法的调用封装：

    ```c++
    template<typename Impl>
    struct object::weak::IColor::methods_impl {
      static struct TString getColor(struct object_IColor_t tobj) {
        return taihe::into_abi<taihe::string>(taihe::cast_data_ptr<Impl>(tobj.data_ptr)->getColor());
      }

      static void setColor(struct object_IColor_t tobj, struct TString c) {
        return taihe::cast_data_ptr<Impl>(tobj.data_ptr)->setColor(taihe::from_abi<taihe::string_view>(c));
      }
    };

    template<typename Impl>
    constexpr object_IColor_ftable object::weak::IColor::ftbl_impl = {
      .getColor = &methods_impl<Impl>::getColor,
      .setColor = &methods_impl<Impl>::setColor,
    };
    ```

10. 上面的 `cast_data_ptr<Impl>` 函数定义在 `object.hpp` 中用于将 `DataBlockHead*` 转换为具体的 `Impl*`，从而可以调用 `Impl` 类中的方法：

    ```c++
    template<typename Impl>
    inline Impl *cast_data_ptr(struct DataBlockHead *data_ptr) {
      return &static_cast<data_block<Impl> *>(data_ptr)->impl;
    }
    ```

需要注意的是，通过上述流程创建出来的对象类型是 `taihe::impl_holder<MyObject, IColor, IShape>`，这其实更像是是一个未被类型擦除的，`Impl` 的智能指针，而不是一个具体的 Taihe 接口对象（`IColor` 或 `IShape`）。该对象还保有 `MyObject` 的编译期类型，所有方法调用都是静态分发的（所以 `taihe::impl_holder<MyObject, IColor, IShape>` 中其实并没有 `vtbl_ptr` 成员），因此可以调用 `MyObject` 的所有方法，包括那些没在 Taihe 接口中声明的方法。

但是，一个 `taihe::impl_holder<MyObject, IColor, IShape>` 对象可以隐式转换为 `IColor`, `IShape` 或者 `IBase`（该对象所实现的所有 Taihe 接口及基接口），从而获得一个真正的 Taihe 接口对象：

```c++
taihe::impl_holder<MyObject, IColor, IShape> obj = ...;
IColor color_obj = obj;          // 隐式转换为 IColor 接口对象（拷贝语义）
IShape shape_obj = obj;          // 隐式转换为 IShape 接口对象（拷贝语义）
IBase base_obj = std::move(obj); // 隐式转换为 IBase 接口对象（移动语义）
```

当尝试将一个 `taihe::impl_holder<...>` 对象隐式转换为某个 Taihe 接口对象（以移动转换为持有者类型为例）时，过程如下：

1. 调用 `impl_holder` 类中的一个模板转换运算符，该运算符接受一个接口持有者类型 `InterfaceHolder` 作为模板参数，并要求该类型满足 `is_holder` 静态成员变量为 `true` 的条件（以确保它是一个持有者类型，而不是借用类型），然后通过 `get_vtbl_ptr<InterfaceHolder>()` 获取针对该接口的虚表指针，并将 `data_ptr` 成员转移给新的接口对象：

    ```c++
    template<typename InterfaceHolder,
            std::enable_if_t<InterfaceHolder::is_holder, int> = 0>
    operator InterfaceHolder() && {
      return InterfaceHolder({
          this->template get_vtbl_ptr<InterfaceHolder>(),
          std::exchange(this->data_ptr, nullptr),
      });
    }
    ```

2. `get_vtbl_ptr<InterfaceHolder>()` 是 `impl_view` 类中的一个模板成员函数，它接受一个接口类型 `InterfaceDest` 作为模板参数，表示要转换到的目标接口类型。该函数通过折叠表达式遍历 `impl_view` 的所有接口类型 `InterfaceTypes...`，检查它们的 `view_type` 是否可以转换为 `InterfaceDest::view_type`，一旦找到一个匹配的接口类型，就使用该接口类型的 `vtbl_impl<Impl>` 来获取对应的虚表指针：

    ```c++
    template<typename InterfaceDest,
        std::enable_if_t<
            (std::is_convertible_v<typename InterfaceTypes::view_type, typename InterfaceDest::view_type> || ...),
            int> = 0>
    static inline typename InterfaceDest::vtable_type const *get_vtbl_ptr() {
      typename InterfaceDest::vtable_type const *vtbl_ptr = nullptr;
      (
          [&] {
            using InterfaceType = InterfaceTypes;
            if constexpr (std::is_convertible_v<typename InterfaceType::view_type, typename InterfaceDest::view_type>) {
              vtbl_ptr = typename InterfaceDest::view_type(
                            typename InterfaceType::view_type({
                                &InterfaceType::template vtbl_impl<Impl>,
                                nullptr,
                            })
                        ).m_handle.vtbl_ptr;
            }
          }(),
          ...);
      return vtbl_ptr;
    }
    ```

#### 3.3.2 静态转换和动态转换

每个 Taihe 接口类（如 `IColor`, `IShape`, `IfancyObj`, `weak::IFancyObj` 等等）都定义了静态转换和动态转换的成员函数，这些函数在 `*.proj.1.hpp` 中生成。

静态转换是隐式的（以 `IFancyObj` 通过移动方式转换为 `IBase` 为例）：

```c++
operator object::IBase() && {
  return object::IBase({
      static_cast_from_IFancyObj_to_IBase(this->m_handle.vtbl_ptr),
      std::exchange(this->m_handle.data_ptr, nullptr),
  });
}
```

并且，所有 Taihe 接口对象都可以被隐式转换为 `taihe::data_holder`（持有者）或 `taihe::data_view`（借用者）类型，它们定义在 `object.hpp` 中，表示一个任意/未知类型的 Taihe 接口对象，只包含 `data_ptr`，没有 `vtbl_ptr`。转换函数同样定义在 `IXxx`, `weak::IXxx` 等类内：

```c++
operator taihe::data_view() const & {
  return taihe::data_view(this->m_handle.data_ptr);
}

operator taihe::data_holder() const & {
  return taihe::data_holder(tobj_dup(this->m_handle.data_ptr));
}
```

此外，每个 Taihe 接口类中也定义了从 `taihe::data_view` 或 `taihe::data_holder` 到该接口的显式动态转换函数（以从 `data_view` 转换为 `weak::IFancyObj` 为例）：

```c++
explicit IFancyObj(::taihe::data_view other)
    : IFancyObj({
          dynamic_cast_to_IFancyObj(other.data_ptr->rtti_ptr),
          other.data_ptr,
      }) {}
```

这样以来，当尝试从 `IBase` 显式转换为 `weak::IFancyObj` 时，会先将 `IBase` 隐式转换为 `data_view`，然后调用 `weak::IFancyObj` 的构造函数完成动态转换。

#### 3.3.3 方法调用

可以直接在 Taihe 接口对象上通过 `operator->` 访问其接口方法：

```c++
IShape shape_obj = ...;
taihe::string color = shape_obj->getShape();
```

1. `operator->` 定义在 `weak::IShape` 类中，并被 `IShape` 类继承。调用时，它会将 `m_handle` 成员（一个 `object_IShape_t` 结构体，包含 `vtbl_ptr` 和 `data_ptr`）的指针强制转换为 `weak::IShape::view_type const *`：

    ```c++
    virtual_type const *operator->() const & {
      return reinterpret_cast<virtual_type const *>(&m_handle);
    }
    ```

2. `weak::IShape::view_type` 的定义在 `proj.2.hpp` 中，其中包含了 `getShape` 方法的实现。在调用时，它会将 `this` 指针重新转换回 `object_IShape_t const *`，然后调用 `call_IShape_getShape` 函数：

    ```c++
    struct ::object::weak::IShape::virtual_type {
      ::taihe::string getShape() const & {
        return ::taihe::from_abi<::taihe::string>(call_IShape_getShape(*reinterpret_cast<object_IShape_t const *>(this)));
      }

      void setShape(::taihe::string_view s) const & {
        return call_IShape_setShape(*reinterpret_cast<object_IShape_t const *>(this), ::taihe::into_abi<::taihe::string_view>(s));
      }
    };
    ```
