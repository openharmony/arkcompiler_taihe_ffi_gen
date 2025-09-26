# Taihe 版本演进的现有规格

## global
- 不支持删除
- 不支持修改函数参数类型或自定义类型中 item 的值和类型
- 支持新增全局函数
- 支持新增自定义类型

## struct 和 union
- 不支持修改、新增和删除

## enum
- 不支持修改原有枚举常量值或类型
- 支持新增枚举常量，必须将新增常量置于最后
  
  考虑到未来可能新增枚举常量，为保证安全，在文档说明中提示用户必须明确写出对 default 情况的处理

## interface
- 不支持新增接口做为原有接口的父接口
- 支持新增接口做为原有接口的子接口
- 支持新增方法（对新增方法位置无限制）

    在 interface 的函数表中存储版本信息，用于判断是否需要调用默认实现，详见 [Interface ABI 函数表的设计](./InterfaceAbi.md#233-函数调用)

    我们可以定义不同版本接口如下：

    ```rust
    // 未标注 version 默认为初始版本
    interface IFoo {
        // 未标注 version 默认为初始版本
        func0(): void;
    } 

    // 标记当前 interface 为 1.0 版本
    @version("1.0")
    interface IFoo {
        func0(): void;
        // 标记当前方法 func1 在大于或等于 1.0 版本的 interface 开始支持
        @version("1.0")
        func1(): void;
    }

    // 标记当前 interface 为 2.0 版本 
    @version("2.0")
    interface IFoo {
        func0(): void;
        // 标记当前方法 func1 在大于或等于 1.0 版本的 interface 开始支持
        @version("1.0")
        func1(): void;
        // 标记当前方法 func2 在大于或等于 2.0 版本的 interface 开始支持
        @version("2.0")
        func2(): void;
    }
    ```
