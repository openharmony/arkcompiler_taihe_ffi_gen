TODO Now:
1. 基于现在的代码结构整理原来的代码生成，同步生成 .d.ts 和 napi.cpp，并在修改 tryit 使其可以快速运行验证  Done
2. 优先支持基础类型，已知 NAPI 的接口里只有对 bool, double, int32, int64, unint32 的接口，那么其他类型应该映射为什么呢
3. 思考 struct, interface 投影到 .d.ts 中是什么数据结构类型
4. register 是应该对一个 IDL 文件夹里面所有文件一起注册还是一个 IDL 文件注册一次，现在是一个 IDL 注册一次，对应每个 taihe 文件都生成一个 .d.ts 和一个 .node

暂时未考虑但影响代码生成的点：
1. a.taihe use b.taihe
2. namespace （为 DTS 涉及自己的 writer 学习 STSWriter 也许可行）


暂时有替代办法待优化的点：
1. 应使用 Json 配置使 .d.ts 和 .node 放在其他目录下也能找到，需探索
2. tryit 里为了实现对每个 taihe 文件生成一个 .node 对文件夹进行了遍历，这是否合适 
