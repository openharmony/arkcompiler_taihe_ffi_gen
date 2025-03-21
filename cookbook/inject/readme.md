### 注入

Taihe的实现侧是在C++层，用户有可能希望在sts侧实现部分面向对象的逻辑，如：

```typescript
class Foo_inner implements Foo {
    // 在sts类内增加member
    name: string = "default";
    // 函数逻辑内使用sts侧成员变量
    with_name(): void {
        console.log(this.name);
    }
    // 函数逻辑侧使用sts侧对象
    with_this(): void {
        console.log(this)
    }
}
```

此时，可以使用Taihe 注入 机制实现

`inject.Taihe`
```taihe
interface Foo {
    inject """
    name: string
"""
    class_inject """
    name: string = "default";
"""
    with_name([sts_member="name"] name: String): void;
    with_this([sts_this] thiz: Opaque): void;
}

function makeFoo(): Foo;
```

1 `inject """ {inject_text} """` 该语法会将 {inject_text} 的内容生成到sts侧接口中

2 `class_inject """ {inject_text} """` 该语法会将 {inject_text} 的内容生成到sts侧接口实现中

3 `[sts_member="{member_name}"]` 该annotation作用在函数参数上，用于将sts侧接口的成员变量作为C++侧函数参数

4 `[sts_this]` 该annotation作用在函数参数上，用于将sts侧接口实现对象作为C++侧函数参数


按C++逻辑完成 作者侧实现
```C++
class Foo {
public:
    void with_name(string_view name) {
        std::cout << name << std::endl;
    }
    void with_this(uintptr_t thiz) {
        std::cout << thiz << std::endl;
    }
};
::inject::Foo makeFoo() {
    return make_holder<Foo, ::inject::Foo>();
}
```

注意到我们生成的`inject.sts`
```typescript
class Foo_inner implements Foo {
    private _vtbl_ptr: long;
    private _data_ptr: long;
    private constructor(_vtbl_ptr: long, _data_ptr: long) {
        this._vtbl_ptr = _vtbl_ptr;
        this._data_ptr = _data_ptr;
    }

    // 2 此处将 name: string = "foo_default_name"; 注入了sts侧
    name: string = "foo_default_name";
    native with_name_inner(name: string): void;
    // 3 此处将sts侧接口的成员变量作为C++侧函数参数
    with_name(): void {
        return this.with_name_inner(this.name);
    }
    native with_this_inner(thiz: NullishType): void;
    // 4 此处将sts侧接口实现对象作为C++侧函数参数
    with_this(): void {
        return this.with_this_inner(this);
    }
}
export interface Foo {
    // 1 此处将name: string注入了sts侧
    name: string
    with_name(): void;
    with_this(): void;
}
native function makeFoo_inner(): Foo;
export function makeFoo(): Foo {
    return makeFoo_inner();
}
```

编号与taihe侧解释对应

`main.ets`
```typescript
let foo = inject.makeFoo();
foo.with_this();
foo.with_name();
console.log("set foo.name = foo_new_name")
foo.name = "foo_new_name";
foo.with_name();
// Log output: 
// 140734359051632
// foo_default_name
// set foo.name = foo_new_name
// foo_new_name
```
