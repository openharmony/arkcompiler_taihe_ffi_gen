### 异步

在看本章内容前，最好对同步和异步有一定的了解。

以javascript为例，简要解释同步与异步
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

其中，`setTimeout`是一个异步函数，arg0是一个函数，arg1是时间，表示在过了一段时间后，执行arg0

简而言之，异步就是不阻塞后面的代码，而是 先执行其他任务，等操作完成后再回来处理

sts提供了异步的支持，但是native并不支持异步

下面我们介绍使用taihe在C++侧按原有逻辑实现，在sts侧生成异步代码并使用

第一步 在taihe文件中声明
```taihe
[gen_async = "add", gen_promise = "add"]
function addSync(a: i32, b: i32): i32;
```

我们可以看到函数addSync上方有一个`[xxx]`, 这是taihe的注解(annotation)语法

taihe annotation语法格式为
```taihe
[xxx = "yyy"]

[xxx("yyy, zzz")]
```

taihe的注解可以作用在变量、函数、interface、struct、以及当前文件上

处理作用在当前文件上时，将注解写在文件末尾，其余情况下都是写在被作用者的上方

回到当前taihe文件，生成sts async 版本函数的注解格式为 `[gen_async = "{async_name}"]`，其中`{async_name}`为sts侧async版本函数的函数名；生成sts promise 版本函数的注解格式为 `[gen_promise = "{promise_name}"]`，其中`{promise_name}`为sts侧promise版本函数的函数名，这两个注解可以单独使用，也可以在interface内的函数使用

注：希望用户对promise有所了解，可以参考javascript的promise

第二步 实现声明的接口
```C++
int32_t addSync(int32_t a, int32_t b) {
    return a + b;
}
```

我们可以在实现侧像写同步代码一样实现函数

第三步 生成并编译

`compiler/`
```sh
./run-test /path/to/async -ani
```

async和promise版本的函数生成在sts侧
```typescript
// 内部函数
native function addSync_inner(a: int, b: int): int;
// 导出的普通函数
export function addSync(a: int, b: int): int {
    return addSync_inner(a, b);
}
// 导出函数的async版本
export function add(a: int, b: int, callback: AsyncCallback<int>): void {
    (launch addSync_inner(a, b))
    .then((ret: NullishType) => {
            let retInner = ret as int;
            let error = new Error();
            callback(error, retInner);
    })
    .catch((ret: NullishType) => {
        let retError = ret as Error;
        callback(retError);
    });
}
// 导出函数的promise版本
export function add(a: int, b: int): Promise<int> {
    return launch addSync_inner(a, b);
}
```

用户侧使用

`main.ets`
```TypeScript
// 使用同步版本的函数
console.log("addSync: ", async_test.addSync(1, 2))

// 使用async版本
async_test.add(10, 20, (error: Error, data?: int) => {
    if (!error.message) {
        console.log("main finsih test async success ", data);
    } else {
        console.log("main finsih test async ERROR ", error);
    }
})

// 使用promise版本
try {
    let retPromise = await async_test.add(0, 2);
    console.log("main finsih test async promise success ")
} catch (error) {
    console.error("main finsih test async promise ERROR ", error)
}
```

#### Know more, Code better

类内函数的异步版本也是同理

taihe文件
```taihe
interface IStringHolder {
    [gen_async="getAsync", gen_promise="getPromise"]
    get(): String;
    [gen_async="setAsync", gen_promise="setPromise"]
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
        .then((ret: NullishType) => {
            let retInner = ret as string;
            let error = new Error();
            callback(error, retInner);
        })
        .catch((ret: NullishType) => {
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
        .catch((ret: NullishType) => {
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
