# 运行时类型模型与扩展协议知识

本文记录运行时数据类型模型，以及类型或接口实现者可以自行实现的扩展协议。固定 ABI、对象内部结构和调用工具也在本文分类，但不称为协议。文件分层见 `Runtime_Architecture_Knowledge_Base_CN.md`；接口实现细节见 `docs/internal/runtime/InterfaceAbi.md`。

## 数据类型整体模型

| 类别 | 代表类型 | ABI 表示 | 参数形式与内存管理 |
| --- | --- | --- | --- |
| 基础类型 | `unit`，标量，枚举 | 标量或固定大小值 | 通常按值；没有独立堆内存。 |
| 复合类型 | 生成的结构体，联合体，`error` | C 结构体或标签联合 | 结构体/联合体参数为 `const&`；按字段语义复制。 |
| 独占堆内存类型 | `optional`, `array` | 指针，或指针加长度 | 作为参数时使用借用类型；复制时深拷贝，移动时转移指针。 |
| 引用计数类型 | `string`, `vector`, `map`, `set`, `future`, `completer` | 指向共享存储的句柄 | 作为参数时传递弱引用类型，通过引用计数管理内存。 |
| 接口类型 | IDL 接口，`callback`，接口化容器 | 胖指针 | 作为参数时传递弱引用类型，通过引用计数管理内存。 |

类型分类由 ABI 表示、复制方式和释放责任共同决定。`expected<T, E>` 是调用结果工具，不是独立 ABI 类型；容器的借用类型通常命名为 `*_view`。

## 类型映射协议

| 协议 | 回答的问题 | 约束 |
| --- | --- | --- |
| `as_abi<T>` / `as_abi_t<T>` | C++ 类型 `T` 的 ABI 存储类型是什么？ | 持有类型与借用类型可以映射到同一 ABI 句柄，但生命周期不同。 |
| `as_param<Owner>` / `as_param_t<Owner>` | 持有类型作为 C++ 参数时使用什么类型？ | 标量/枚举通常按值，结构体/联合体为 `const&`，容器和接口通常使用借用类型。 |

## 固定 ABI 与调用工具

| 工具 | 方向 | 职责 |
| --- | --- | --- |
| `as_abi_func<Return, Params...>` | C++ 签名到 ABI 函数指针 | 按固定规则展开参数、返回值和错误输出参数。 |
| `into_abi<T>` | C++ 到 ABI | 将值、借用对象或引用转换为 `as_abi_t<T>`。 |
| `from_abi<T>` | ABI 到 C++ | 按 `T` 的投影和所有权约定恢复调用侧值。 |
| `function_calling_convention` | ABI 入口到 C++ 自由函数 | 生成从 ABI 调用到 C++ 实现的适配函数。 |
| `method_calling_convention` | ABI 入口到实现对象方法 | 从接口句柄取得 `Impl` 并调用成员函数。 |
| `call_abi_func` | C++ 调用到 ABI 函数指针 | 组织参数、返回值和 `expected` error 通道。 |

- 调用约定与 `call_abi_func` 的类型必须一一对应；`expected` 的错误输出参数必须在调用两侧完成分配和释放。

## 接口类型实现协议

`callback_view` 和生成的接口借用类型都实现下面的要求，`object.hpp` 据此把 `Impl` 包装为接口对象：

| 实现者提供 | 消费位置 | 要求 |
| --- | --- | --- |
| ABI 句柄构造和 `m_handle` | 接口转换与调用代码 | 句柄包含虚表指针和数据指针；借用类型不增加引用计数。 |
| `is_holder`, `view_type`, `holder_type`, `abi_type`, `vtable_type` | `impl_view` / `impl_holder` | 区分持有与借用类型，并公开接口相关类型。 |
| `ftbl_impl<Impl>`, `vtbl_impl<Impl>` | `impl_view::get_vtbl_ptr()` | 为具体 `Impl` 提供函数表和虚表。 |
| `qiid_impl<Impl>(InterfaceId)` | `impl_view::qiid()` | 返回当前接口或祖先接口的虚表；不支持时返回空指针。 |
| 父接口转换、`data_view` / `data_holder` 转换 | 静态转换和对象身份操作 | 转换时必须保持同一数据指针，并按持有语义增减引用计数。 |

新增接口化类型时必须实现这组要求。优先对照 `callback.hpp` 和生成的 `*.proj.1.hpp`；`DataBlockHead` 和 `TypeInfo` 不是接口协议。

## 对象内部结构与工具

| 分类 | 数据或工具 | 作用 |
| --- | --- | --- |
| ABI 与存储 | `DataBlockHead`, `TypeInfo`, `data_block<Impl>`, `make_data_ptr`, `cast_data_ptr` | 保存对象元数据并分配、访问实现对象。 |
| 生命周期工具 | `tobj_init`, `tobj_dup`, `tobj_drop` | 管理数据块引用计数。 |
| 通用句柄 | `data_*`, `type_*`, `impl_*`, `make_holder` | 管理类型擦除、实现类型和接口集合。 |

- 借用类型不增加引用计数；从借用类型构造持有类型时必须增加引用计数。
- 持有类型移动时必须清空源指针，析构时必须且只能释放一次。
- 不要让 `data_*` 等低信息句柄隐式恢复已经擦除的实现类型或接口集合。
- `TypeInfo` 的函数必须围绕同一 `DataBlockHead` 身份；运行时 ABI 和生成器不得单边修改。
- 修改 `.abi.h`、类型映射或调用约定时，必须验证已有生成代码的编译和运行。

## 修改前检查

| 问题 | 决策 |
| --- | --- |
| 新类型属于哪种 ABI 和内存管理类别？ | 先确定复制、移动、借用和释放责任。 |
| 它的 ABI 表示和参数投影是什么？ | 再定义 `as_abi` / `as_param`，不要从一者推断另一者。 |
| 是否新增接口化类型？ | 对照 `callback` 和生成接口，逐项实现接口类型协议。 |
| 是否改变运行时 ABI？ | 必须运行 ABI 和跨语言互操作回归。 |

## 代码和测试

| 主题 | 锚点 |
| --- | --- |
| 类型映射与容器 | `runtime/include/taihe/{common,optional,array,vector,map,set,string,async}.hpp`, `compiler/taihe/codegen/{abi,cpp}/analyses.py` |
| 接口类型协议示例 | `runtime/include/taihe/callback.hpp`, `test/rgb/generated/include/*.proj.1.hpp` |
| 对象内部结构与工具 | `runtime/include/taihe/object.{abi.h,hpp}` |
| ABI 值和调用适配 | `runtime/include/taihe/invoke.hpp` |
| 详细设计与回归 | `docs/internal/runtime/InterfaceAbi.md`, `test/object/`, `test/ani_callback/`, `test/napi_callback/` |