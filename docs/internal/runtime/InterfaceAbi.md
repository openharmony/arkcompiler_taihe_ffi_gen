# Taihe Interface ABI 设计文档

## Taihe IDL 示例代码

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

## 对象构成

一个 Taihe 接口对象由两个指针构成，它们分别指向**虚表**和**数据块**。

```c
struct IFancyObj {
  struct IFancyObj_vtable const* vtbl_ptr;  // 指向虚表
  struct DataBlockHead* data_ptr;           // 指向数据块头
};
```

### 虚表

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

### 函数表

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

### 数据块

Taihe 接口对象的**数据块**则由**数据头**和**实际对象内存**两部分构成，其中**数据头**存储了对象的**运行时类型信息**（RTTI）和**引用计数**等元数据。

```c
struct DataBlockHead {
  struct TypeInfo const *rtti_ptr;  // 指向运行时类型信息
  TRefCount m_count;                // 引用计数
};

struct DataBlock {
  struct DataBlockHead head;        // 数据块头
  // 实际对象内存，包含用户具体实现类里的数据
};
```

### 运行时类型信息

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

### 接口 ID

**接口 ID** 是一个全局唯一的标识符，在运行时对 Taihe 接口对象进行动态转换时会根据此标识判断该对象是否实现了特定接口。每个在 Taihe IDL 中声明的接口在编译时都会分配一个唯一的 ID。

```c
void const *IBase_iid = ...;
void const *IColor_iid = ...;
void const *IShape_iid = ...;
void const *IFancyObj_iid = ...;
```

## 方法

### 静态转换

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

### 动态转换

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

### 函数调用

函数调用通过虚表中的函数指针实现。调用时，首先获取对象的虚表指针，然后根据接口的函数表指针调用相应的方法。

```cpp
void call_IFancyObj_sparkle(struct IFancyObj self) {
  self->vtbl_ptr->ftbl_ptr_0->sparkle(self);
}
```

### 对象的构造、拷贝和销毁

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

### 对象的哈希和比较

对象的哈希和比较通过 `TypeInfo` 中的 `hash_fptr` 和 `same_fptr` 函数指针实现。这些函数指针在对象的运行时类型信息中定义，允许在运行时对对象进行哈希和比较操作。

```cpp
size_t tobj_hash(struct DataBlockHead *data_ptr) {
  return data_ptr->rtti_ptr->hash_fptr(data_ptr);
}

bool tobj_same(struct DataBlockHead *left_ptr, struct DataBlockHead *right_ptr) {
  return left_ptr->rtti_ptr->same_fptr(left_ptr, right_ptr);
}
```
