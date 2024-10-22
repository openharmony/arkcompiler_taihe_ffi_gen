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
|  vt_ptr   |
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

* ft_ptr指向该接口自己的函数表, 函数表内为函数指针

```
IColor_ft_ptr————————>---------------
                     |  GetColor()  |
                     |--------------|
                     |  SetColor()  |
                      --------------

IShape_ft_ptr————————>---------------
                     |  GetShape()  |
                     |--------------|
                     |  SetShape()  |
                      --------------
```

----------------------------------------------

data_ptr指向数据块, 数据块由`DataBlockHead`和`ObjectData`构成

```
data_ptr————————>-------------
                |DataBlockHead|
                |-------------|
                |  ObjectData |
                 -------------
```

dataBlockHead组成如下: 

```C
// Maybe unuse dataBlockHead
                 -------------
                |    ti_ptr   |
                |-------------|
                |    m_count  |
                 -------------
```

m_count用于引用计数, 而ti_ptr是一个指向TypeInfo类型的指针, TypeInfo用于存储对象类型的相关信息

```
ti_ptr——————————>-----------------------
                |         version       |
                |-----------------------|
                |           len         |
                |-----------------------|
                |          dup()        |
                |-----------------------|
                |          drop()       |
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

### create dup drop

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

dup函数用于复制，需要管理引用计数

```C
struct obj obj_dup(struct class obj) {
   ++obj.data_ptr->m_count;
   dup_f();
}
```

drop函数用于删除

```C
void obj_drop(struct class obj) {
   if (obj.data_ptr && --(objptr.data->m_count) == 0) {
      free_f();
   }
}
```

To be continued...
