# obj设计文档

## 继承关系举例

```
////////////////////
/////  IBase  //////
///   /     \  /////
// IColor  IShape //
////  \     /  /////
//// IRectangle ////
////////////////////
```

## 对象构成

* 一个Object由两个指针构成，一个指针为vt_ptr，一个指针为data_ptr

```
[IRectangleObject]
------------
|   vt_ptr  |
------------
|  data_ptr |
------------
```

* vt_ptr指向一个表

```
vt_ptr——————————>------------------
                | IBase_ft_ptr     |
                |------------------|
                | IColor_ft_ptr    |
                |------------------|
                | IBase_ft_ptr     |
                |------------------|
                | IShape_ft_ptr    |
                |------------------|
                | IRectangle_ft_ptr|
                 ------------------
```

* ft_ptr指向该接口自己的函数表, 函数表内，第一个元素为函数指针数量，剩下的成员为函数指针

```
IColor_ft_ptr————————>---------------
                     |     len      |
                     |--------------|
                     |  GetColor()  |
                     |--------------|
                     |  SetColor()  |
                      --------------

IShape_ft_ptr————————>---------------
                     |     len      |
                     |--------------|
                     |  GetShape()  |
                     |--------------|
                     |  SetShape()  |
                      --------------
```

----------------------------------------------

`data_ptr`指向数据块, 数据块由`DataBlockHead`和`ObjectData`构成

```
data_ptr————————>-------------
                |DataBlockHead|
                |-------------|
                |  ObjectData |
                 -------------
```

`DataBlockHead`组成如下: 

```C
// Maybe unuse dataBlockHead
                 -------------
                |    ti_ptr   |
                |-------------|
                |    m_count  |
                 -------------
```

`m_count`用于引用计数, 而`ti_ptr`是一个指向`TypeInfo`类型的指针, `TypeInfo`用于存储对象类型的相关信息

```
ti_ptr——————————>-----------------------
                |         version       |
                |-----------------------|
                |           len         |
                |-----------------------|
                | pre_idmap_func_count  |
                |-----------------------|
                |       free_data()     |
                |-----------------------|
                | IBaseId      | vt_ptr |
                |-----------------------|
                | IColorId     | vt_ptr |
                |-----------------------|
                | IShapeId     | vt_ptr |
                |-----------------------|
                | IRectangleId | vt_ptr |
                 -----------------------
```

## 功能部分

### ABI稳定性

目前的oop设计支持的版本演进的相关功能有：

✔️ 给已有的interface方法后增加新的方法

✔️ 修改已有的interface方法的实现

✔️ 在已有的成员变量后增加新的成员变量


### static_cast and dynamic_cast

类型转换与虚表结构紧密关联, 因为虚表结构的特殊设计, 使得对象拥有了static_cast的能力

```C
// Rectangle_obj
vt_ptr——————————>------------------
                | IBase_ft_ptr     |
                |------------------|
                | IColor_ft_ptr    |
             // |------------------|
             // | IBase_ft_ptr     |
             // |------------------|
             // | IShape_ft_ptr    |
             // |------------------|
                | IRectangle_ft_ptr|
                 ------------------ 

// 上面vt_ptr指向的vt 


// IRectangle的vt结构体如下：
struct IRectangle_vt {
   // obj_IColor_vt
   ft_ptr* IBase_ft_ptr;
   ft_ptr* IColor_ft_ptr;
   // obj_IRectangle_vt
   ft_ptr* IBase_ft_ptr;
   ft_ptr* IShape_ft_ptr;

   ft_ptr* IRectangle_ft_ptr;
};

// IShape的vt结构体如下：
struct IRectangle_vt {
   ft_ptr* IBase_ft_ptr;
   ft_ptr* IShape_ft_ptr;
};


// example
obj->vt = obj->vt.obj_IRectangle_vt
```

### 调用函数
```C
// obj function
obj.vt_ptr->obj_func(obj.data_ptr);
// interface function
obj.vt_ptr.obj_IRectangle_vt->getShape(obj.data_ptr);
```

### create addref release

create函数用于在堆上申请空间并在对应数据处赋值

注：目前的设计typeinfo指针也需要使用者自行赋值

```C
// create
struct ClassDataBlock* class_data_create(arg...) {
   size_t bytes_requires = sizeof(struct ClassDataBlock);
   struct ClassDataBlock* data_ptr = malloc(bytes_requires);
   data_ptr->head.ti_ptr = (struct typeInfo*)&obj_class_typeInfo;
   data_ptr->head.dup_func = ...;
   data_ptr->head.drop_func = ...;
   data_ptr->head.m_count = 1;
   // data
   data_ptr->data.arg1 = arg1;
   data_ptr->data.arg2 = arg2;
   data_ptr->data.arg3 = arg3;
   return data_ptr;
}
```

增加引用计数

```C
void tobj_addref(struct TObject tobj) {
  if (tobj.data_ptr && tobj.data_ptr->m_count != 0) {
    ++tobj.data_ptr->m_count;
  }
}
```

释放函数

```C
void tobj_release(struct TObject tobj) {
  if (tobj.data_ptr && --(tobj.data_ptr->m_count) == 0) {
    tobj.data_ptr->rtti_ptr->free_data(tobj);
    tobj.data_ptr = NULL;
    tobj.vtbl_ptr = NULL;  
  }
}
```

### 支持interface的方法带有默认实现, 并在运行时生成完整虚表

```C
// Old version
interface IBase {
   void func_1() {
      ...
   }
};

void call_funcs(IBase inst) {
   inst.func_1();
}

// New version
interface IBase {
   void func_1() {
      ...
   }

   // new function !
   void func_2() {
      ...
   }
};

void call_funcs(IBase inst) {
   inst.func_1();
   inst.func_2(); // new !
}
```

当使用old version的.h与new version的.dll时，会找不到func_2()的符号

于是解决这个问题就需要有两个条件

* 1 虚表里有`func_2()`

* 2 `func_2()`需要有实现

所以运行时要在更新一遍虚表，新增的interface方法**必须**带有默认实现

#### 运行时生成虚表方案

运行时生成虚表需要考虑的问题是**是否支持interface方法默认实现的覆写**

##### 支持覆写
如果支持interface覆写函数，那就需要在code generate时需要对一个class和它的继承关系拓扑排序，然后在运行时的生成虚表相关代码可能会有如下情况：

```C
//   IA
//  /  \
// IB  IC
//  \  /
//   D

if (D.has_func()) {
    // ...
} else if (IB.has_func()) {
    // ...
} else if (IC.has_func()) {
    // ...
} else if (IA.has_func()) {
    // ...
}
```
继承关系复杂时，对性能会有较大影响

##### 不支持覆写
如果不支持覆写，则认为IA.func1()和IB.func1()并不是一个函数

此时虚表大小会比支持覆写的情况大一些

```C
// 允许覆写
struct IA_ftable {
    void(*func1)();
}

struct IB_ftable {
    void(*func2)();
}

// 不允许覆写
struct IA_ftable {
    void(*func1)();
}

struct IB_ftable {
    void(*func1)();
    void(*func2)();
}
```

但是因为每个ftable只会存自身的函数，所以运行时只需要考虑class实现以及interface自身默认实现两种情况

```C
if (D.has_func()) {
    // ...
} else if (IX.has_func()) {
    // ...
}
```

只会有2分支，分支数相比明显降低

目前taihe采用不支持覆写的版本，接口的函数部分应该更像一个contract，不应依赖于函数的实现，同时促进组合而非继承。


###
—————————————————————————————————————————————————

To be continued...
