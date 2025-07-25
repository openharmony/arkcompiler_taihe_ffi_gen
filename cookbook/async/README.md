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
@static_overload("add")
@async function addAsync(a: i32, b: i32): i32;

@static_overload("add")
@promise function addPromise(a: i32, b: i32): i32;

function addSync(a: i32, b: i32): i32;
```

我们可以看到函数 `addSync` 上方有一个 `@xxx()`, 这是 taihe 的注解（annotation）语法

- Taihe 的注解非常灵活
  - `@!foobar` 添加注解到 当下的词法空间下，而 `@foobar`（注意，没有感叹号）将注解添加到下一个元素中。
  - 例如，`@foobar struct Foo {}` 等价于 `struct Foo { @!foobar }`，都是在给 `struct Foo` 添加注解。
  - 注解可以有参数，例如 `@foobar("baz")` 或 `@foobar(1, "baz")`
  - 无参数时，括号可以省略，例如 `@foobar()` 等同于 `@foobar`

taihe 的注解可以作用在变量、函数、interface、struct、以及当前文件上

处理作用在当前文件上时，将注解写在文件末尾，其余情况下都是写在被作用者的上方

回到当前 taihe 文件，在 sts 中生成 async 版本函数的注解格式为 `@async`；生成 sts promise 版本函数的注解格式为 `@promise`，这两个注解单独使用，也可以在 interface 内的函数使用

taihe 不允许同名函数，如果用户有同名的函数，需要使用 `@static_overload("<new_name>")` 注解，该注解的作用是在 ets 侧生成 `export overload <new_name> { func1, func2}`，由此实现 java-like 重载

此外，用户如果希望在 sts 侧函数名进行改变，而不希望使用 overload，可以使用 `@rename("<new_name>")` 注解，该注解的作用是改变生成在 ets 侧的对应函数名

注：希望用户对 promise 有所了解，可以参考 javascript 的 promise

## 第二步 实现声明的接口
```C++
int32_t addSync(int32_t a, int32_t b) {
    return a + b;
}

TH_EXPORT_CPP_API_addAsync(addSync);
TH_EXPORT_CPP_API_addPromise(addSync);
TH_EXPORT_CPP_API_addSync(addSync);
```

我们可以在实现侧像写同步代码一样实现函数

## 第三步 生成并编译

```sh
# 注：taihe 文件里的函数与 C++ 规范一致，所以函数会在生成的 ets 侧自动转变为小写字母开头函数
# taihe 文件中的写法：
#   function FooBar(): void;
# 生成的 ets 侧代码
#   function fooBar(): void;
# 如果希望生成的 ets 侧函数与 taihe 文件一致，可以使用 --sts-keep-name
taihe-tryit test -u sts path/to/async --sts-keep-name
```

async 和 promise 版本的函数生成在 sts 侧
```typescript
// 导出的 Async 函数
export function addAsync(a: int, b: int, callback: AsyncCallback<int>): void {
    taskpool.execute((): int => {
        return _taihe_addAsync_native(a, b);
    })
    .then((ret: Any): void => {
        callback(null, ret as int);
    })
    .catch((ret: Any): void => {
        callback(ret as BusinessError, undefined);
    });
}
// 导出的 Promise 函数
export function addPromise(a: int, b: int): Promise<int> {
    return new Promise<int>((resolve, reject): void => {
        taskpool.execute((): int => {
            return _taihe_addPromise_native(a, b);
        })
        .then((ret: Any): void => {
            resolve(ret as int);
        })
        .catch((ret: Any): void => {
            reject(ret as Error);
        });
    });
}
// 导出的同步函数
export function addSync(a: int, b: int): int {
    return _taihe_addSync_native(a, b);
}
export overload add {
    addAsync,
    addPromise,
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

类内函数的异步版本也是类似

taihe 文件
```taihe
interface IStringHolder {
    @async getAsync(): String;
    @promise getPromise(): String;
    @rename("newGet")
    get(): String;

    @static_overload("set")
    @async setAsync(a: String): void;
    @static_overload("set")
    @promise setPromise(a: String): void;
    setSync(a: String): void;
}

function makeIStringHolder(): IStringHolder;
```

C++ 实现
```C++
class IStringHolder {
public:
  IStringHolder() : str("MyStr") {}

  ~IStringHolder() {}

  string get() {
    return str;
  }

  ::taihe::string getAsync() {
      return str;
  }

  ::taihe::string getPromise() {
      return str;
  }

  void setSync(string_view a) {
    this->str = a;
  }

  void setAsync(::taihe::string_view a) {
    this->str = a;
  }

  void setPromise(::taihe::string_view a) {
    this->str = a;
  }

private:
  string str;
};
::async::IStringHolder makeIStringHolder() {
    return taihe::make_holder<IStringHolder, ::async::IStringHolder>();
}
```

sts 侧 export
```typescript
export interface IStringHolder {
    // get 函数 Async 版
    getAsync(callback: AsyncCallback<string>): void;
    // get 函数 Promise 版
    getPromise(): Promise<string>;
    // get 函数 Sync 版，rename 函数
    newGet(): string;
    // set 函数 Async 版
    setAsync(a: string, callback: AsyncCallback<void>): void;
    // set 函数 Promise 版
    setPromise(a: string): Promise<void>;
    // set 函数 Sync 版
    setSync(a: string): void;
    // java-like 重载
    overload set {
        setAsync,
        setPromise,
    }
    _taihe_getAsync_revert(): string {
        throw new Error(`No valid revert function found`);
    }
    _taihe_getPromise_revert(): string {
        throw new Error(`No valid revert function found`);
    }
    _taihe_get_revert(): string {
        return this.get();
    }
    _taihe_setAsync_revert(a: string): void {
        throw new Error(`No valid revert function found`);
    }
    _taihe_setPromise_revert(a: string): void {
        throw new Error(`No valid revert function found`);
    }
    _taihe_setSync_revert(a: string): void {
        return this.setSync(a);
    }
}
class _taihe_IStringHolder_inner implements IStringHolder {
    private _taihe_vtblPtr: long;
    private _taihe_dataPtr: long;
    private _taihe_register(): void {
        _taihe_registry.register(this, this._taihe_dataPtr, this);
    }
    private _taihe_unregister(): void {
        _taihe_registry.unregister(this);
    }
    private _taihe_initialize(vtblPtr: long, dataPtr: long): void {
        this._taihe_vtblPtr = vtblPtr;
        this._taihe_dataPtr = dataPtr;
        this._taihe_register();
    }
    public _taihe_copyFrom(other: _taihe_IStringHolder_inner): void {
        this._taihe_initialize(other._taihe_vtblPtr, _taihe_objDup(other._taihe_dataPtr));
    }
    public _taihe_moveFrom(other: _taihe_IStringHolder_inner): void {
        this._taihe_initialize(other._taihe_vtblPtr, other._taihe_dataPtr);
        other._taihe_unregister();
    }
    native _taihe_getAsync_native(): string;
    native _taihe_getPromise_native(): string;
    native _taihe_get_native(): string;
    native _taihe_setAsync_native(a: string): void;
    native _taihe_setPromise_native(a: string): void;
    native _taihe_setSync_native(a: string): void;
    getAsync(callback: AsyncCallback<string>): void {
        taskpool.execute((): string => {
            return this._taihe_getAsync_native();
        })
        .then((ret: Any): void => {
            callback(null, ret as string);
        })
        .catch((ret: Any): void => {
            callback(ret as BusinessError, undefined);
        });
    }
    getPromise(): Promise<string> {
        return new Promise<string>((resolve, reject): void => {
            taskpool.execute((): string => {
                return this._taihe_getPromise_native();
            })
            .then((ret: Any): void => {
                resolve(ret as string);
            })
            .catch((ret: Any): void => {
                reject(ret as Error);
            });
        });
    }
    // rename 函数
    newGet(): string {
        return this._taihe_get_native();
    }
    setAsync(a: string, callback: AsyncCallback<void>): void {
        taskpool.execute((): void => {
            return this._taihe_setAsync_native(a);
        })
        .then((ret: Any): void => {
            callback(null, ret as undefined);
        })
        .catch((ret: Any): void => {
            callback(ret as BusinessError, undefined);
        });
    }
    setPromise(a: string): Promise<void> {
        return new Promise<void>((resolve, reject): void => {
            taskpool.execute((): void => {
                return this._taihe_setPromise_native(a);
            })
            .then((ret: Any): void => {
                resolve(ret as undefined);
            })
            .catch((ret: Any): void => {
                reject(ret as Error);
            });
        });
    }
    setSync(a: string): void {
        return this._taihe_setSync_native(a);
    }
    overload set {
        setAsync,
        setPromise,
    }
    _taihe_getAsync_revert(): string {
        throw new Error(`No valid revert function found`);
    }
    _taihe_getPromise_revert(): string {
        throw new Error(`No valid revert function found`);
    }
    _taihe_get_revert(): string {
        return this.get();
    }
    _taihe_setAsync_revert(a: string): void {
        throw new Error(`No valid revert function found`);
    }
    _taihe_setPromise_revert(a: string): void {
        throw new Error(`No valid revert function found`);
    }
    _taihe_setSync_revert(a: string): void {
        return this.setSync(a);
    }
}
```
