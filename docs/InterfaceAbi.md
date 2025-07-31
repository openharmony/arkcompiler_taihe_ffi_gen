# OOP ABI 设计文档

## Taihe IDL 示例代码

以一个菱形继承的场景为例，假设我们有一个接口 `IFancyObj`，它继承了两个接口 `IColor` 和 `IShape`，而这两个接口又都继承自 `IBase`。我们可以定义如下的接口：
```rust
interface IBase {
  getState(): bool;
  setState(s: bool): ();
}

interface IColor: IBase {
  getColor(): String;
  setColor(c: String): ();
}

interface IShape: IBase {
  getShape(): String;
  setShape(s: String): ();
}

interface IFancyObj: IColor, IShape {
  sparkle(): ();
}
```

## 对象构成

一个 Taihe 接口对象由两个指针构成，分别指向虚表和数据块。其中虚表存储了接口的函数指针，而数据块存储了对象的实际数据。
```c
struct IFancyObj {
    struct IFancyObj_vtable const* vtbl_ptr;  // 指向虚表
    struct DataBlockHead* data_ptr;           // 指向数据块头
};
```

其中，`vtbl_ptr` 指向该对象对应接口（Interface）的虚表（_vtable），虚表中的内存如下：
```c
struct IFancyObj_vtable {
    struct IFancyObj_ftable const* ftbl_ptr_0;  // 指向 IFancyObj 的函数表
    struct IColor_ftable const* ftbl_ptr_1;     // 指向 IColor 的函数表
    struct IBase_ftable const* ftbl_ptr_2;      // 指向 IBase 的函数表
    struct IShape_ftable const* ftbl_ptr_3;     // 指向 IShape 的函数表
    struct IBase_ftable const* ftbl_ptr_4;      // 指向 IBase 的函数表
};
```

其中，每个 `ftbl_ptr` 则指向相应接口的函数表（_ftable）, 每个函数表内部存有这个接口自己声明的所有方法的指针：
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

`data_ptr` 指向数据块，每个数据块由 `DataBlockHead` 和 `ObjectData` 两部分构成，其中，`DataBlockHead` 存储了对象的运行时类型信息和引用计数等元数据，而 `ObjectData` 则存储了对象的实际数据。
```c
struct DataBlockHead {
  struct TypeInfo const *rtti_ptr;  // 指向运行时类型信息
  TRefCount m_count;                // 引用计数
};
```

`rtti_ptr` 指向运行时类型信息（`TypeInfo`），它包含了对象的版本信息、销毁函数指针、动态转换表长度和动态转换表等信息。
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

## 方法

### 静态转换

接口的函数表由若干函数指针构成，函数指针按照它们在 IDL 接口中的声明顺序排列。

对于在 IDL 中定义的每个接口，其虚表结构体中的第一项应是指向该接口的函数表结构体的指针，接下来则应按顺序排入该接口*直接*继承的所有父接口的虚表中的完整内存排布，如果多个父接口同时继承了同一祖先，则该祖先的函数表指针也应当在子接口的虚表中出现多次。这保证了一个接口的虚表可以被*静态*转换为其任一祖先的虚表。

以下是 `IFancyObj` 接口和它的父接口的静态转换函数示例：
```cpp
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

struct IBase_vtable const* static_cast_from_IFancyObj_to_IColor(struct IFancyObj_vtable const* vtbl_ptr) {
  if (vtbl_ptr == NULL) {
    return NULL;
  }
  return (struct IBase_vtable const*)((void* const*)vtbl_ptr + 4);
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

每个对象的数据块头部都有指向其具体类型运行时信息（`typeinfo`）的指针。在 `typeinfo` 中存有版本信息 `version`，`free` 函数指针（用于销毁对象），动态转换表的长度 `len` 和动态转换表。动态转换表是从 Interface ID 到相应虚表的映射，用于在运行时查询对象实现的所有接口，从而实现运行时的向下转换。

以下是一个样例：
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
  tref_set(&data_ptr->m_count, 1);
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
