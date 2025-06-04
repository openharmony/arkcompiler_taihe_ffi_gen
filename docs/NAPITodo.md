NAPI 代码生成及验证：
1. 修改 tryit 支持运行 Done （遗留问题一）
2. 参照现有代码生成架构实现生成 .napi.cpp 和 .d.ts 支持以下语言特性
    - [x] 基础类型                                            (遗留问题二)
    - [x] struct 
    - [ ] struct 继承                                          (需要用 attr，是否和 ani 使用同样方案待确认)
    - [x] interface
    - [x] interface 继承
    - [ ] ts 侧绑定构造函数 class(interface / struct)           (本周)
    - [ ] class, static, constructor, readonly
    - [ ] enum                                                 (下一步)
    - [ ] union                                                (下一步)
    - [ ] undefined, null
    - [ ] array
    - [ ] map set vector
    - [ ] namespace
    - [x] callback
    - [x] optional
    - [ ] override
    - [ ] promise, async
    - [ ] bigint
    - [ ] arraybuffer

**注意：现在的验证方式是基于 ts 和 napi 非鸿蒙 napi，应配置鸿蒙环境下验证的方法，测试编译验证方法待设计。**

遗留问题：
1. .d.ts 和 .node 的存放位置，暂时存放在 author_generated 目录下，（main.js 也存放在此），main.ts 调用需注意
2. 已知 NAPI 的接口里只有对 bool, double, int32, int64, unint32 的接口，其他类型应该映射为？

暂时未考虑但影响代码生成的点：
1. a.taihe use b.taihe
2. namespace （为 DTS 设计自己的 writer 学习 STSWriter 也许可行）


暂时有办法待优化的点：
1. 应使用 Json 配置使 .d.ts 和 .node 放在其他目录下也能找到，需探索
2. tryit 里为了实现对每个 taihe 文件生成一个 .node 对文件夹进行了遍历，这是否合适 
3. test/napi 应拆解为多个 test case 例如 napi_primitives, napi_struct 等，另外里面现存在一些 interget.d.ts 等文件，等自动生成部分完成将统一删除
