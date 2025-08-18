NAPI 代码生成及验证：
1. 修改 tryit 支持运行 Done （遗留问题一）
2. 参照现有代码生成架构实现生成 .napi.cpp 和 .d.ts 支持以下语言特性
    - [x] 基础类型
    - [x] struct 
    - [x] struct 继承                                    (和 ani 使用了同样方案)
    - [x] interface
    - [x] interface 继承
    - [x] ts 侧绑定构造函数 class(struct)
    - [x] ts 侧绑定构造函数 class(interface)              (只支持绑定一个构造函数且无法继承 interface)
    - [x] static
    - [x] readonly
    - [x] get set
    - [x] const
    - [x] enum
    - [x] union                                          (number|string|bool|array|map)
    - [x] undefined, null                               # TODO: 适配新的类型
    - [x] array
    - [x] record
    - [x] map                                           (规格为不保序)
    - [ ] set vector
    - [x] namespace
    - [x] callback
    - [x] optional
    - [ ] override
    - [ ] promise, async
    - [x] bigint
    - [x] arraybuffer
    - [x] typedarray
    - [x] import
    - [x] Opaque
    - [ ] inject
    - [ ] on_off

3. 需要报错但未实现或实现的较为简单，设计如何报错并区分如何：
    - [ ] Record 的 key 类型限制，TS 语法规定是 string/number，SDK 现有场景是 string
    - [ ] ctor 检查返回值为 指定的 interface 且检查这个 interface 为 class 
    - [ ] 检查 Union 要么有指定类型，要么有 undefined/null 的注解
    - [ ] 检查 struct 的基类是否是 struct
    - [ ] 检查 @static 是否加在 class 上
    - [ ] 检查 class 必须有 ctor

TODO:
1. 生命周期，之前已做: done
2. 错误处理，发现错误抛出 error: done
3. NAPI doc: 草稿已有 [NapiUsageGuide](./NapiUsageGuide.md)，各功能全覆盖，细节待完善
4. 逃逸通道: Opaque + dts_type 已支持，inject 待支持
5. union 自定义类型，tag

**注意：现在的验证方式是基于 ts 和 napi 非鸿蒙 napi，应配置鸿蒙环境下编译验证方法待设计。**
xml 例子编译运行成功


暂时有办法待优化的点：
1. tryit 里为了实现对每个 .d.ts 文件生成一个 .node 文件进行了遍历，这是否合适 
2. napi_get_and_clear_last_exception 返回的 exception maybe is napi_undefined
