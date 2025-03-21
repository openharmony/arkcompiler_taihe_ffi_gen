### 回调

回调(Callback)可以理解为把一个函数作为参数传给另一个函数，在合适的时机再调用它

Taihe的callback样例如下

`callback.taihe`
```taihe
function cb_void_void(f: () => void): void;
function cb_i_void(f: (a: i32) => void): void;
function cb_str_str(f: (a: String) => String): String;

struct Person {
  name: String;
  age: i32;
}

function cb_struct(f: (data: Person) => Person): void;
```

我们可以看到 `({param_type}) => {return_type}` 格式的语句就是一个函数，在上面把一个函数作为参数传递给了另外一个函数
上述样例介绍无参数无返回值、有参数无返回值、有参数有返回值以及以struct作为参数和返回值4种情况

`callback.impl.cpp`
```C++
void cb_void_void(callback_view<void()> f) {
    f();
}
void cb_i_void(callback_view<void(int32_t)> f) {
    f(1);
}
string cb_str_str(callback_view<string(string_view)> f) {
    taihe::core::string out = f("hello");
    return "hello";
}
void cb_struct(callback_view<::callback::Person(::callback::Person const&)> f) {
    ::callback::Person result = f(::callback::Person{"Tom", 18});
    std::cout<< result.name << " " << result.age << std::endl;
    return;
}
```

`main.ets`
```typescript
callback_lib.cb_void_void(() => {
    console.log("void input void output callback!");
});
callback_lib.cb_i_void((a: int) => {
    console.log("int input void output callback! input is: ", a);
});
let result = callback_lib.cb_str_str((a: string) => {
    console.log("param a is: ", a);
    return "my return value";
});
console.log("global function output: ", result);
callback_lib.cb_struct((a: callback_lib.Person) => {
    let person = new callback_lib.Person(a.name + " Swift", a.age + 18 ); 
    return person;
});
```

To be Continued