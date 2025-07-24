# null 与 undefined

在 taihe 中，使用 union 与注解 @null、@undefined 声明 null 类型与 undefined 类型

## 第一步：编写接口原型

**File: `idl/nullabletype.taihe`**
```taihe
union NullableValue {
    sValue: String;
    iValue: i32;
    @undefined uValue;
    @null nValue;
}

function makeNullableValue(tag: i32): NullableValue;
```
如上所示，Taihe IDL 文件中为一个 union 内的变量名前增加 注解 @null、@undefined 来声明 null 类型与 undefined 类型

## 第二步：完成 C++ 实现

**File: `author/src/nullabletype.impl.cpp`**
```C++
constexpr int32_t TAG_NULL = 0;
constexpr int32_t TAG_STRING = 1;
constexpr int32_t TAG_INT = 2;

::nullabletype::NullableValue makeNullableValue(int32_t tag) {
    switch (tag) {
        case TAG_NULL:
            return ::nullabletype::NullableValue::make_nValue();
        case TAG_STRING:
            return ::nullabletype::NullableValue::make_sValue("hello");
        case TAG_INT:
            return ::nullabletype::NullableValue::make_iValue(123);
        default:
            return ::nullabletype::NullableValue::make_uValue();
    }
}
```

使用 union 的 make 方法创建 null 或 undefined

对于 taihe union 的 C++ 侧方法参考

[Taihe C++ 教程](../taihe_cpp/README.md)

[Taihe Union 相关教程样例](../enum_union/README.md)

## 第三步：在 ets 侧使用

```typescript
let nvalue = makeNullableValue(0);
console.log("null: " + nvalue);
let svalue = makeNullableValue(1);
console.log("string: " + svalue);
let ivalue = makeNullableValue(2);
console.log("int: " + ivalue);
let uvalue = makeNullableValue(10);
console.log("undefined: " + uvalue);
```

输出结果：
```sh
null: null
string: hello
int: 123
undefined: undefined
```