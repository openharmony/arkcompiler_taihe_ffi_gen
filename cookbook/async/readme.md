# 异步

在看本章内容前，最好对同步和异步有一定的了解。

以 javascript 为例，简要解释同步与异步
```js
// 同步
console.log("1");
console.log("2");
console.log("3");

// output:
// 1
// 2
// 3

// 异步
console.log("1");

setTimeout(() => {
    console.log("2");
}, 1000);

console.log("3");

// output:
// 1
// 3
// 2
```

其中，`setTimeout` 是一个异步函数，`arg0` 是一个回调函数，`arg1` 是时间，表示在过了一段时间后，执行 `arg0`

简而言之，异步就是不阻塞后面的代码，而是 先执行其他任务，等操作完成后再回来处理

sts 提供了异步的支持，但是 native 并不支持异步

下面我们介绍使用 taihe 在 C++ 侧按原有逻辑实现，在 sts 侧生成异步代码并使用

## 第一步 在 taihe 文件中声明
```taihe
@gen_async("add")
@gen_promise("add")
function addSync(a: i32, b: i32): i32;
```

我们可以看到函数addSync上方有一个 `@xxx()`, 这是 taihe 的注解（annotation）语法

- Taihe 的注解非常灵活
  - `@!foobar` 添加注解到 当下的词法空间下，而 `@foobar`（注意，没有感叹号）将注解添加到下一个元素中。
  - 例如，`@foobar struct Foo {}` 等价于 `struct Foo { @!foobar }`，都是在给 `struct Foo` 添加注解。
  - 注解可以有参数，例如 `@foobar("baz")` 或 `@foobar(1, "baz")`
  - 无参数时，括号可以省略，例如 `@foobar()` 等同于 `@foobar`

taihe 的注解可以作用在变量、函数、interface、struct、以及当前文件上

处理作用在当前文件上时，将注解写在文件末尾，其余情况下都是写在被作用者的上方

回到当前 taihe 文件，在 sts 中生成 async 版本函数的注解格式为 `@gen_async("<async_name>")`，其中 `<async_name>` 为 sts 侧 async 版本函数的函数名；生成 sts promise 版本函数的注解格式为 `@gen_promise("<promise_name>")`，其中 `<promise_name>` 为 sts 侧 promise 版本函数的函数名，这两个注解可以单独使用，也可以在 interface 内的函数使用

注：希望用户对 promise 有所了解，可以参考 javascript 的 promise

## 第二步 实现声明的接口
```C++
int32_t addSync(int32_t a, int32_t b) {
    return a + b;
}
```

我们可以在实现侧像写同步代码一样实现函数

## 第三步 生成并编译

`compiler/`
```sh
./run-test /path/to/async -ani
```

async 和 promise 版本的函数生成在 sts 侧
```typescript
// 内部函数
native function addSync_inner(a: int, b: int): int;
// 导出的普通函数
export function addSync(a: int, b: int): int {
    return addSync_inner(a, b);
}
// 导出函数的 async 版本
export function add(a: int, b: int, callback: AsyncCallback<int>): void {
    (launch addSync_inner(a, b))
    .then((ret: Any) => {
            let retInner = ret as int;
            let error = new Error();
            callback(error, retInner);
    })
    .catch((ret: Any) => {
        let retError = ret as Error;
        callback(retError);
    });
}
// 导出函数的 promise 版本
export function add(a: int, b: int): Promise<int> {
    return launch addSync_inner(a, b);
}
```

用户侧使用

`main.ets`
```TypeScript
// 使用同步版本的函数
console.log("addSync: ", async_test.addSync(1, 2))

// 使用 async 版本
async_test.add(10, 20, (error: BusinessError | null, data?: int) => {
    if (error !== null && error.code !== 0) {
        console.log("main finsih test async ERROR ", error);
    } else {
        console.log("main finsih test async success ", data);
    }
})

// 使用 promise 版本
try {
    let retPromise = await async_test.add(0, 2);
    console.log("main finsih test async promise success ")
} catch (error) {
    console.error("main finsih test async promise ERROR ", error)
}

// Log output:
// addSync:  3
// async success  30
// async promise success 
// MyStr
// interface async success 
// interface async success p_istringholder  interface async set
```

#### Know more, Code better

类内函数的异步版本也是同理

taihe文件
```taihe
interface IStringHolder {
    @gen_async("getAsync")
    @gen_promise("getPromise")
    get(): String;
    @gen_async("setAsync")
    @gen_promise("setPromise")
    set(a: String): void;
}

function makeIStringHolder(): IStringHolder;
```

C++实现
```C++
class IStringHolder {
public:
    IStringHolder() : str("MyStr") {}
    ~IStringHolder() {}
    string get() {
        return str;
    }
    void set(string_view a) {
        this->str = a;
    }
private:
    string str;
};
::async::IStringHolder makeIStringHolder() {
    return make_holder<IStringHolder, ::async::IStringHolder>();
}
```

sts侧export
```typescript
class IStringHolder_inner implements IStringHolder {
    private _vtbl_ptr: long;
    private _data_ptr: long;
    private constructor(_vtbl_ptr: long, _data_ptr: long) {
        this._vtbl_ptr = _vtbl_ptr;
        this._data_ptr = _data_ptr;
    }
    // get函数c++实现对应
    native get_inner(): string;
    // get函数普通版本
    get(): string {
        return this.get_inner();
    }
    // get函数async版本
    getAsync(callback: AsyncCallback<string>): void {
        (launch this.get_inner())
        .then((ret: Any) => {
            let retInner = ret as string;
            let error = new Error();
            callback(error, retInner);
        })
        .catch((ret: Any) => {
            let retError = ret as Error;
            callback(retError);
        });
    }
    // get函数promise版本
    getPromise(): Promise<string> {
        return launch this.get_inner();
    }
    // set函数c++实现对应
    native set_inner(a: string): void;
    // get函数普通版本
    set(a: string): void {
        return this.set_inner(a);
    }
    // get函数async版本
    setAsync(a: string, callback: AsyncCallback<void>): void {
        (launch this.set_inner(a))
        .then((): void => {
            let error = new Error();
            callback(error);
        })
        .catch((ret: Any) => {
            let retError = ret as Error;
            callback(retError);
        });
    }
    // get函数promise版本
    setPromise(a: string): Promise<void> {
        return launch this.set_inner(a);
    }
}
export interface IStringHolder {
    get(): string;
    getAsync(callback: AsyncCallback<string>): void;
    getPromise(): Promise<string>;
    set(a: string): void;
    setAsync(a: string, callback: AsyncCallback<void>): void;
    setPromise(a: string): Promise<void>;
}
```
