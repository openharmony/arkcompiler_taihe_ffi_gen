# OOP ABI 设计文档

## 继承关系举例

```
interface IBase {
   fn getState(): bool;
   fn setState(s: bool): ();
}

interface IColor: IBase {
   fn getColor(): String;
   fn setColor(c: String): ();
}

interface IShape: IBase {
   fn getShape(): String;
   fn setShape(s: String): ();
}

interface IFancyObj: IColor, IShape {
   fn sparkle(): ();
}
```

## 对象构成

一个 Object 由两个指针构成，其中第一个指针为 `vt_ptr`，第二个指针为 `data_ptr`

```
[IFancyObjObject]

+----------------+
|     vt_ptr     |
|----------------|
|    data_ptr    |
+----------------+
```

其中，`vt_ptr` 指向该对象对应接口（Interface）的虚表（VTable），虚表中的内存如下：

```
vt_ptr --------> +------------------+
                 | IFancyObj_ft_ptr |
                 |------------------|
                 | IColor_ft_ptr    |
                 |------------------|
                 | IBase_ft_ptr     |
                 |------------------|
                 | IShape_ft_ptr    |
                 |------------------|
                 | IBase_ft_ptr     |
                 +------------------+
```

其中，每个 `ft_ptr` 则指向相应接口的函数表（FTable）, 每个函数表内部存有这个接口自己声明的所有方法的指针：

```
IColor_ft_ptr -----> +--------------+
                     |  getColor()  |
                     |--------------|
                     |  setColor()  |
                     +--------------+

IShape_ft_ptr -----> +--------------+
                     |  getShape()  |
                     |--------------|
                     |  setShape()  |
                     +--------------+
```

`data_ptr` 指向数据块, 每个数据块由 `DataBlockHead` 和 `ObjectData` 两部分构成

```
data_ptr ---------> +---------------+
                    | DataBlockHead |
                    |---------------|
                    | ObjectData    |
                    +---------------+
```

其中 `dataBlockHead` 的组成如下: 

```
+----------------+
|    ti_ptr      |
|----------------|
|    m_count     |
+----------------+
```

`m_count` 用于引用计数, `ti_ptr` 是一个指向 `typeinfo` 的指针, `typeinfo` 内存储有与对象类型相关的运行时信息

```
ti_ptr ----> +----------------------+
             |       version        |
             |----------------------|
             |       free()         |
             |----------------------|
             |       len            |
             |----------------------|
             | IBaseId     | vt_ptr |
             |----------------------|
             | IColorId    | vt_ptr |
             |----------------------|
             | IShapeId    | vt_ptr |
             |----------------------|
             | IFancyObjId | vt_ptr |
             +----------------------+
```

## 功能部分

### ABI 稳定性

### 静态转换

接口的函数表由若干函数指针构成，函数指针按照它们在 IDL 接口中的声明顺序排列。

对于在 IDL 中定义的每个接口，其虚表结构体中的第一项应是指向该接口的函数表结构体的指针，接下来则应按顺序排入该接口*直接*继承的所有父接口的虚表中的完整内存排布，如果多个父接口同时继承了同一祖先，则该祖先的函数表指针也应当在子接口的虚表中出现多次。这保证了一个接口的虚表可以被*静态*转换为其任一祖先的虚表。

以下是从基于前文所给例子生成的 C ABI 中截取的部分片段：

```C
// IBase 的函数表结构体定义
struct IBaseFT {
  bool (*getState)();
  void (*setState)(bool s);
};

// ...

// IBase 的虚表结构体定义
struct IBaseVT {
  IBaseFT*      IBase_ft_ptr;
};

// IColor 的虚表结构体定义
struct IColorVT {
  IColorFT*     IColor_ft_ptr;
  IBaseFT*      IBase_ft_ptr;
};

// IShape 的虚表结构体定义
struct IShapeVT {
  IShapeFT*     IShape_ft_ptr;
  IBaseFT*      IBase_ft_ptr;
};

// IFancyObj 的虚表结构体定义
struct IFancyObjVT {
  IFancyObjFT*  IFancyObj_ft_ptr;
  IColorFT*     IColor_ft_ptr;
  IBaseFT*      IBase_ft_ptr_0;
  IShapeFT*     IShape_ft_ptr;
  IBaseFT*      IBase_ft_ptr_1;
};

// 可以直接将 IFancyObj_vt_ptr 转换为相应的 IShapeObj_vt_ptr 或 IBase_vt_ptr
struct IShape_vt* IShape_vt_ptr = (void **)IFancyObj_vt_ptr + offsetof(IFancyObjVT, IShape_ft_ptr);
struct IBase_vt* IBase_vt_ptr = (void **)IFancyObj_vt_ptr + offsetof(IFancyObjVT, IBase_ft_ptr_0);
```

### 动态转换

每个对象的数据块头部都有指向其具体类型运行时信息（`typeinfo`）的指针。在 `typeinfo` 中存有版本信息 `version`，`free` 函数指针（用于销毁对象），动态转换表的长度 `len` 和动态转换表。动态转换表是从 Interface ID 到相应虚表的映射，用于在运行时查询对象实现的所有接口，从而实现运行时的向下转换。

以下是一个样例：

```C
inline struct IFancyObj dynamic_cast_to_IFancyObj(struct DataBlockHead* data_ptr) {
  struct TypeInfo *rtti_ptr = data_ptr->rtti_ptr;
  struct IFancyObj result;
  for (size_t i = 0; i < rtti_ptr->len; i++) {
    if (rtti_ptr->idmap[i].id == IFancyObj_iid) {
      result.vtbl_ptr = (struct IFancyObjVT*)rtti_ptr->idmap[i].vtbl_ptr;
      result.data_ptr = data_ptr;
      return result;
    }
  }
  result.vtbl_ptr = NULL;
  result.data_ptr = NULL;
  return result;
}
```

### 调用函数

```C
obj.vt_ptr->IFancyObj_ft_ptr->sparkle(obj.data_ptr);
obj.vt_ptr->IBase_ft_ptr_0->setState(obj.data_ptr, 1);
```

To be continued...
