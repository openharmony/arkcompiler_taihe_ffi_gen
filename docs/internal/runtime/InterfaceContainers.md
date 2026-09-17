# 接口化容器与共享数组类型设计

**摘要** Taihe 现有 `Array`、`Vector`、`Map`、`Set` 主要表达本地值容器或运行时内建容器语义。它们适合传递容器快照，但不适合直接承载上层虚拟机已有的大容器，也不适合表达两侧共同维护的共享状态。本文设计 `SharedVector<T>`、`SharedSequence<T>`、`SharedMap<K, V>`、`SharedSet<K>` 与 `SharedArray<T>`：前四者是接口化容器代理，按需访问上层对象；`SharedArray<T>` 是类似 `String` 的共享连续内存封装，直接携带数据指针和共享生命周期。旧容器保持兼容，新类型用于表达新的代理与共享存储语义。

## 1. 背景与问题

现有容器在跨语言转换时通常会遍历内部元素并逐项转换。这个策略简单，但会把成本前置到参数传递阶段：即使调用方只访问少量元素，仍然需要为整个容器付出转换和分配成本；嵌套容器还会进一步放大这个问题。

旧容器也无法表达活跃共享状态。`Array` / `Vector` / `Map` / `Set` 按值或本地容器语义工作，两侧拿到的是各自的容器对象；一侧后续修改不会自然反映到另一侧。对于 JS、ArkTS 等上层 VM 中已有的容器对象，这不是用户想要的“代理同一个对象”。

另一方面，旧容器已经有 C++ 投影和 ABI 预期。对 `Vector`、`Map`、`Set` 来说，是否必须新增独立的 `SharedVector`、`SharedMap`、`SharedSet` 还不是最终结论；理论上也可以逐步把旧类型改为接口化容器。但无法确定是否已有用户依赖旧 C++ 投影的本地容器行为，例如 `vector::operator[]` 返回稳定引用，或容器迭代器解引用返回可写的非常量左值引用。接口化容器如果封装的是上层 VM 对象，就无法保证这些引用语义。因此，当前先新增独立类型，把兼容风险隔离开。

`SharedArray` 的动机不同。它不是为了保留旧 `Array` 的接口习惯，而是表达另一种所有权模型：旧 `Array<T>` 是值数组，持有类型拥有一份自己的连续存储；`SharedArray<T>` 描述一段可以被多个对象或上层运行时共享的连续内存。这个差异不能只靠修改旧 `Array` 的方法集表达。

## 2. 设计原则

这组类型首先是桥层协议，不是最终 C++ API。协议方法表示后端必须能绑定和实现的能力；`accept(visitor)`、C++ iterator、`operator[]`、抛异常适配等更符合语言习惯的接口，应由投影层在原始协议之上提供。

设计时权衡了以下几个目标：

- 语义正确性：类型名和接口应准确表达是否共享、是否连续、是否可变长、是否只是上层对象代理。
- 性能：常见操作尽量用一次或少量跨桥调用完成。
- 易用性：方法语义应贴近主流容器心智模型，例如 list/map/set、插入、删除、遍历等。
- 简洁性：避免为每个投影层语法糖都扩展桥协议。

有些方法虽然可以组合出来，但仍值得进入协议。`forEachItem` 可以把遍历从大量 `get` 调用变成一次跨桥过程；`getAndRemove`、`tryGetAndRemove` 可以把“取旧值”和“修改”放进一次跨桥调用，避免 TOCTOU 问题。相反，C++ iterator、`operator[]`、`keys` / `items` 这类能力如果可以由默认实现或投影层自然组合，就不强制每个实现类手写。

## 3. 总体方案

### 3.1 新增类型

新增五个内建类型：

| IDL 类型 | C++ 持有类型 | C++ 借用类型 | ABI 类型 | 形态 | 类型参数约束 |
| --- | --- | --- | --- | --- | --- |
| `SharedVector<T>` | `taihe::shared_vector<T>` | `taihe::shared_vector_view<T>` | `TSharedVector` | 接口胖指针 | `T` 为非 `void` 类型 |
| `SharedSequence<T>` | `taihe::shared_sequence<T>` | `taihe::shared_sequence_view<T>` | `TSharedSequence` | 接口胖指针 | `T` 为非 `void` 类型 |
| `SharedMap<K, V>` | `taihe::shared_map<K, V>` | `taihe::shared_map_view<K, V>` | `TSharedMap` | 接口胖指针 | `K`、`V` 为非 `void` 类型 |
| `SharedSet<K>` | `taihe::shared_set<K>` | `taihe::shared_set_view<K>` | `TSharedSet` | 接口胖指针 | `K` 为非 `void` 类型 |
| `SharedArray<T>` | `taihe::shared_array<T>` | `taihe::shared_array_view<T>` | `TSharedArray` | 特殊对象 | `T` 为标量类型 |

目标文件命名如下：

| 类型 | ABI 头 | C++ 头 | 运行时源文件 |
| --- | --- | --- | --- |
| `SharedVector<T>` | `runtime/include/taihe/shared_vector.abi.h` | `runtime/include/taihe/shared_vector.hpp` | 无 |
| `SharedSequence<T>` | `runtime/include/taihe/shared_sequence.abi.h` | `runtime/include/taihe/shared_sequence.hpp` | 无 |
| `SharedMap<K, V>` | `runtime/include/taihe/shared_map.abi.h` | `runtime/include/taihe/shared_map.hpp` | 无 |
| `SharedSet<K>` | `runtime/include/taihe/shared_set.abi.h` | `runtime/include/taihe/shared_set.hpp` | 无 |
| `SharedArray<T>` | `runtime/include/taihe/shared_array.abi.h` | `runtime/include/taihe/shared_array.hpp` | `runtime/src/shared_array.cpp` |

`SharedVector`、`SharedSequence`、`SharedMap`、`SharedSet` 都表示对上层容器对象或本地实现对象的接口化引用。当前运行时可以用类似 `callback` 的接口对象句柄承载：

```c
struct TContainer {
    struct TContainerVTable const *vtbl_ptr;
    struct DataBlockHead *data_ptr;
};
```

采用这套机制可以复用 Taihe 面向对象机制。C++ 投影仍遵循现有惯例：`*_view` 是借用类型，不增加引用计数；持有类型从 view 构造时增加引用计数，析构时释放引用。

### 3.2 可选方法与默认实现

接口化容器引入可选方法机制，文档中用 `@default` 标记。可选方法仍属于接口协议，但具体实现类可以不直接实现。

ABI 绑定时，如果实现类没有提供某个可选方法（为了与忘记实现、错误实现区分，需要在实现类中手动将该方法声明为静态成员变量 `taihe::use_default`），则该函数表槽填 `nullptr`，这可以利用 invoke.hpp 中提供的 `method_as_abi_func_optional_v` 来实现。调用时先检查函数指针：如果为空则执行默认实现并返回，否则才调用实现类版本。默认实现以接口为单位提供，通常通过同一接口中的基础方法组合出来。

这个机制用于平衡性能和实现成本。`items`、`keys`、`checkedInsert`、`tryGetAndRemove` 等方法常用且可组合；高性能实现可以覆盖默认逻辑，普通实现只需要实现最小核心方法。

### 3.3 错误通道

原则是：只要一个方法在语义上可能失败，就不标 `@noexcept`。在 Taihe 接口描述中，不写 `@noexcept` 表示方法可能返回错误；C++ 投影返回 `expected<T, E>` 或 `expected<void, E>`，但 `expected` 本身不写进 IDL 返回类型。

要区分可处理错误和运行时基本假设失败。越界、key 不存在、目标容器只读、外部对象拒绝写入、代理对象无法完成某个容器操作，是用户可能理解并处理的语义错误，应进入错误通道。虚拟机失效、引用对象损坏、内部句柄悬空等不是用户可恢复错误，不应包装成可处理错误。

**当前，所有方法均不标 `@noexcept`，因此 C++ 投影都返回 `expected<T, E>` 或 `expected<void, E>`。**

返回值上，`Optional<T>` 用来表达“没有这个元素”，错误通道用来表达“这次操作失败”。例如 `IMap.tryGet(key): Optional<V>` 在 C++ 中会投影为 `expected<optional<V>, E>`：`none` 表示查询成功但 key 不存在，`error` 表示查询失败。

### 3.4 C++ 惯用封装层

协议表中列出的是桥层原始接口。C++ 包装类应在这些原始接口之上提供更符合 C++ 使用习惯的封装，例如更自然的命名、预期成功时的 `unwrap` / 抛异常适配、visitor 辅助、或者基于 `forEachItem` 的遍历封装。这层不改变 ABI，也不要求后端额外实现，只是组合已有协议。

不能强行模拟做不到的 C++ 语义。`SharedVector`、`SharedSequence`、`SharedMap` 可能代理上层 VM 对象，无法稳定返回本地元素引用。因此暂不提供会暗示本地引用的接口，例如返回 `T&` 的 `operator[]`，或可解引用为非常量左值引用的 iterator。若未来能用 `forEach` 加 Boost.Coroutine2 `pull_type` 包装出满足 iterator traits 的只读或值迭代器，可以作为 C++ 便利能力加入。

`SharedArray` 是例外。它直接持有连续内存，因此适合提供 `operator[]`，返回真实的 `T&` 或 `T const&`。

### 3.5 C++ 封装层注意事项

对于所有未标注 `@noexcept` 的方法和回调函数，C++ 投影应当返回 `expected<T, error>`，包括 `forEach` 系列方法的访问器。

在 Taihe 中，每个语义类型在 C++ 投影中都分为持有类型和借用类型。其中，通常只有在函数或方法的参数位置才会使用借用类型，返回值和成员变量则一般使用持有类型。在 C++ util 层提供了 `as_param<T>` 模板，以从持有类型推导出对应的借用类型。

在接口化容器的 C++ 投影类型，`shared_vector<T>`、`shared_sequence<T>`、`shared_map<K, V>`、`shared_set<K>` 中，模板参数 `T`、`K`、`V` 都应当是持有类型。但是，在容器的协议方法中，`T`、`K`、`V` 在参数位置出现时，则应该使用 `as_param<T>`、`as_param<K>`、`as_param<V>`，另外，`forEach` 系列方法中访问器的参数也应当使用 `callback_view<expected<bool, error>(as_param<T>)`。

由于这些新容器都是共享且可变的，因此，判等和哈希函数的语义应当是“引用相等”，而不是“值相等”。例如，`SharedArray` 的 `operator==` 应比较 `data()` 和 `length()`，而不是逐元素比较。其余接口化容器不需要专门实现判等和哈希函数，采用 Taihe 接口统一的默认机制即可。

## 4. 容器协议

### 4.1 SharedVector

`SharedVector<T>` 是可变长、按索引访问、但不承诺连续内存的顺序容器。它不提供 `data()`，因为它可能只是上层 VM 数组对象的代理。

协议方法如下：

| 方法 | 协议签名 | 语义 |
| --- | --- | --- |
| `getSize` | `getSize(): u64` | 返回元素数量。 |
| `get` | `get(index: u64): T` | 取指定位置元素；index 越界是语义错误。 |
| `set` | `set(index: u64, value: T): void` | 覆盖指定位置元素。 |
| `getAndSet`* | `@default getAndSet(index: u64, value: T): T` | 覆盖指定位置元素并返回旧值。 |
| `insert` | `insert(index: u64, value: T): void` | 在指定位置插入元素。 |
| `remove` | `remove(index: u64): void` | 移除指定位置元素。 |
| `getAndRemove`* | `@default getAndRemove(index: u64): T` | 移除并返回指定位置元素。 |
| `insertLast`* | `@default insertLast(value: T): void` | 在末尾追加元素。 |
| `removeLast`* | `@default removeLast(): void` | 移除末尾元素。 |
| `getAndRemoveLast`* | `@default getAndRemoveLast(): T` | 移除并返回末尾元素。 |
| `clear` | `clear(): void` | 清空容器。 |
| `getItems` | `getItems(): Array<T>` | 返回普通数组快照。 |
| `forEachItem`* | `@default forEachItem(visitor: (index: u64, value: T) => bool): void` | 顺序遍历；visitor 返回 `false` 时提前停止。 |

`getAndSet`、`getAndRemove`、`getAndRemoveLast` 用于把“取旧值”和“修改”合并成一次跨桥操作，避免两次调用之间容器被重入修改。保留返回 `void` 的 `set`、`remove`、`removeLast`，是为了避免调用方不需要旧值时仍被迫转换旧值。

`forEachItem` 接收的访问器并没有使用 `@noexcept`，因此在 C++ 投影中的返回值类型应为 `expected<bool, E>`，返回 `true` 表示继续遍历，返回 `false` 表示提前停止，返回 `error` 表示访问器执行失败，应当将错误向上传递出 `forEachItem` 方法。

### 4.2 SharedSequence（待定，暂不实现）

`SharedSequence<T>` 是定长、按索引访问、但不承诺连续内存的顺序容器。它用于表达上层固定长度数组或 tuple-like sequence 的懒代理语义。

最初只计划提供 `SharedVector<T>`。后来加入 `SharedSequence<T>`，主要是因为 ArkTS 1.2 有 `FixedArray` 这类类型。`FixedArray` 的元素是装箱类型，不适合用 `SharedArray<T>`；它又不可变长，不能支持 `insertLast`、`removeLast`、`insert`、`remove`、`clear` 等接口。

备选方案是仍用 `SharedVector<T>` 承载 `FixedArray`，变长方法被调用时运行时抛错。这个方案实现更省类型，但代价是类型不够安全，API 表面也会暗示一些实际不支持的能力。而拆出 `SharedSequence<T>` 的代价则是类型系统、codegen 和后端投影更复杂，而且实际应用中 `SharedSequence<T>` 的使用场景可能不多。最终是否保留还需评估。

协议方法如下：

| 方法 | 协议签名 | 语义 |
| --- | --- | --- |
| `getSize` | `getSize(): u64` | 返回元素数量。 |
| `get` | `get(index: u64): T` | 取指定位置元素；index 越界是语义错误。 |
| `set` | `set(index: u64, value: T): void` | 覆盖指定位置元素。 |
| `getAndSet`* | `@default getAndSet(index: u64, value: T): T` | 覆盖指定位置元素并返回旧值。 |
| `getItems` | `getItems(): Array<T>` | 返回普通数组快照。 |
| `forEachItem`* | `@default forEachItem(visitor: (index: u64, value: T) => bool): void` | 顺序遍历；visitor 返回 `false` 时提前停止。 |

`SharedSequence` 和 `SharedArray` 的区别在内存语义：`SharedSequence` 只保证顺序和索引访问，不保证连续存储，也不提供 `data()`。

### 4.3 SharedMap

`SharedMap<K, V>` 是键值映射。

协议方法如下：

| 方法 | 协议签名 | 语义 |
| --- | --- | --- |
| `getSize` | `getSize(): u64` | 返回键值对数量。 |
| `has` | `has(key: K): bool` | 判断 key 是否存在。 |
| `tryGet` | `tryGet(key: K): Optional<V>` | 查询 key，不存在则返回 `none`。 |
| `upsert` | `upsert(key: K, value: V): void` | 新增或覆盖 key 对应值。 |
| `checkedInsert`* | `@default checkedInsert(key: K, value: V): bool` | 插入 key，并返回是否插入成功。 |
| `tryGetAndUpsert`* | `@default tryGetAndUpsert(key: K, value: V): Optional<V>` | 覆盖或插入，并在 key 原本存在时返回旧值。 |
| `tryGetAndInsert`* | `@default tryGetAndInsert(key: K, value: V): Optional<V>` | 仅不存在时插入；key 已存在时返回已有值，插入成功时返回 `none`。 |
| `remove` | `remove(key: K): void` | 删除 key。 |
| `checkedRemove`* | `@default checkedRemove(key: K): bool` | 删除 key，并返回是否删除。 |
| `tryGetAndRemove`* | `@default tryGetAndRemove(key: K): Optional<V>` | 删除 key，并返回旧值；key 不存在则返回 `none`。 |
| `clear` | `clear(): void` | 清空映射。 |
| `getKeys` | `getKeys(): Array<K>` | 返回 key 的普通数组快照。 |
| `forEachKey`* | `@default forEachKey(visitor: (key: K) => bool): void` | 遍历 key；visitor 返回 `false` 时提前停止。 |
| `getValues` | `getValues(): Array<V>` | 返回 value 的普通数组快照。 |
| `forEachValue`* | `@default forEachValue(visitor: (value: V) => bool): void` | 遍历 value；visitor 返回 `false` 时提前停止。 |
| `getEntries` | `getEntries(): Array<SharedMapEntry<K, V>>` | 返回键值对的普通数组快照。 |
| `forEachEntry`* | `@default forEachEntry(visitor: (key: K, value: V) => bool): void` | 遍历键值对；visitor 返回 `false` 时提前停止。 |

`tryGetAnd*` 系列避免常见的“先查再改”跨桥组合。`tryGetAndInsert` 的返回值设计为 `Optional<V>`：key 已存在时返回旧值，插入成功时返回 `none`。如果像 `setDefault` 那样总是返回最终值，那么插入成功时只是把调用方刚传入的对象再传出一次，会产生不必要的对象往返。

`SharedMap` 不提供 `operator[]`。上层 VM 映射对象无法返回稳定的 C++ 左值引用，且 `operator[]` 的缺失即插入语义会隐藏一次写操作。

### 4.4 SharedSet

`SharedSet<K>` 是集合容器。

协议方法如下：

| 方法 | 协议签名 | 语义 |
| --- | --- | --- |
| `getSize` | `getSize(): u64` | 返回元素数量。 |
| `has` | `has(key: K): bool` | 判断元素是否存在。 |
| `insert` | `insert(key: K): void` | 添加元素。 |
| `checkedInsert`* | `@default checkedInsert(key: K): bool` | 插入元素，并返回是否插入。 |
| `remove` | `remove(key: K): void` | 删除元素。 |
| `checkedRemove`* | `@default checkedRemove(key: K): bool` | 删除元素，并返回是否删除。 |
| `clear` | `clear(): void` | 清空集合。 |
| `getKeys` | `getKeys(): Array<K>` | 返回元素的普通数组快照。 |
| `forEachKey`* | `@default forEachKey(visitor: (key: K) => bool): void` | 遍历元素；visitor 返回 `false` 时提前停止。 |

无返回值的 `insert` / `remove` 用于不关心集合大小是否变化的路径；`checkedInsert` / `checkedRemove` 用于需要知道结果的路径。后者可以默认通过 `has` 和基础修改方法组合出来，也可以由后端直接实现以避免多次跨桥调用。

## 5. SharedArray

`SharedArray<T>` 和旧 `Array<T>` 的根本区别在所有权：`Array<T>` 是值数组，作为持有类型时拥有一份自己的连续存储；`SharedArray<T>` 是共享数组对象，可以指向堆内存、外部对象或静态数据，并通过句柄记录共享状态。

| 语义模型\内存管理模型 | 非引用计数、独占或引用 | 引用计数、本地堆存储 | 引用计数、代理对象 |
| --- | --- | --- | --- |
| 不可变长、允许直接访问原始数据指针 | `Array<T>` | `SharedArray<T>` | `SharedArray<T>` |
| 不可变长、不允许访问原始数据指针 | \ | \ | `SharedSequence<T>` |
| 可变长、不允许访问原始数据指针 | \ | `Vector<T>` | `SharedVector<T>` |

`SharedArray<T>` 只允许标量元素，因为只有标量才有稳定跨语言内存布局。它的设计类似 `String`：句柄里直接保存数据指针、长度和共享状态，而不是把元素访问建模为普通容器协议。

只有 `SharedArray` 适合在 C++ 投影里提供 `operator[]`。它的 `data()` 指向连续内存，`operator[]` 可以返回真实的 `T&` 或 `T const&`；`SharedVector`、`SharedSequence` 和 `SharedMap` 都可能只是上层 VM 对象代理，不能返回稳定本地引用。

ABI 结构：

```c
struct TSharedArray {
    uint32_t flags;
    uint32_t byte_length;
    void *data;
    union {
        struct TSharedArrayInternalControlBlock *internal_cb;
        struct TSharedArrayAcquiredControlBlock *acquired_cb;
        struct TSharedArrayAcquireCache *acquire_cache;
    };
};
```

`byte_length` 保存字节长度，而不是元素数量。原因是：它和 `String` 的 C ABI 更接近；更容易对应 TypedArray / ArrayBuffer；未来可以用不同元素类型解释同一段内存，或用 offset 加 byte length 派生子数组；C ABI 本身也不知道泛型参数 `T`。

`data` 直接存在句柄中。曾考虑把 `data` 做成控制块里的取址函数，以支持外部对象内存地址移动的场景。但这样会增加 ABI 和投影复杂度，而且用户拿到指针后仍然很难保证使用期间地址稳定。当前主要目标是 ArrayBuffer / TypedArray 这类地址稳定的对象，因此直接保存 `data` 指针。

存储模式是私有复制策略，不决定公开的生命周期职责：`shared_array` 是 holder，必须释放；`shared_array_view` 是 borrowed view，没有释放职责，其生命周期不得超过依赖的 holder 或静态缓冲区。

| 模式 | `flags` | 控制块 | 复制策略 |
| --- | --- | --- | --- |
| 静态数据 | `TSHARED_ARRAY_STORAGE_STATIC` | 无 | 复制静态值。 |
| 堆内存 | `TSHARED_ARRAY_STORAGE_INTERNAL` | `TSharedArrayInternalControlBlock` | 共享内部缓冲区。 |
| 已 acquire 外部对象 | `TSHARED_ARRAY_STORAGE_ACQUIRED` | `TSharedArrayAcquiredControlBlock` | 共享已 acquire 的 global ref。 |
| 可 acquire borrowed view | `TSHARED_ARRAY_STORAGE_ACQUIRABLE_BORROWED` | `TSharedArrayAcquireCache` | 第一次复制时 acquire，此后共享缓存的 acquired control block。 |

C API 保持 `tarr_*` 前缀：

| 函数 | 作用 |
| --- | --- |
| `tarr_data(TSharedArray)` | 返回原始 `void *` 数据地址。 |
| `tarr_byte_length(TSharedArray)` | 返回字节长度。 |
| `tarr_is_empty(TSharedArray)` | 判断字节长度是否为 0。 |
| `tarr_is_valid(TSharedArray)` | 判断句柄是否有效。 |
| `tarr_set_invalid(TSharedArray *)` | 将责任已转移的句柄标记为无效。 |
| `tarr_new_internal(byte_length)` | 创建持有未初始化堆内存的 holder。 |
| `tarr_new_acquired(data, byte_length, ctx)` | 从已 acquire 的 global ref 创建 holder，并在成功或失败时消费该引用。 |
| `tarr_new_acquirable_borrowed(data, byte_length, ctx, cache)` | 创建带共享 acquire cache 的 borrowed view。 |
| `tarr_new_static(data, byte_length)` | 创建可视作 holder 或 borrowed view 的静态值。 |
| `tarr_subview(TSharedArray, byte_offset, byte_length)` | 派生 borrowed view，不增加引用计数。 |
| `tarr_dup(TSharedArray)` | 从任意 shared array 值创建独立 holder。 |
| `tarr_drop(TSharedArray)` | 消费一个 holder 的释放职责；不得传入 borrowed view。 |
| `tarr_acquire_cache_drop(cache)` | 释放 cache 持有的 acquired control block 引用。 |

`common.hpp` 提供 `static_flag_t` 和 `static_flag`，供 `String` 或 `SharedArray` 构造静态或全局对象引用。`shared_array_view` 和 `shared_array` 都应支持这种构造方式。

`shared_array_view<T>` 不提供无生命周期协议的裸 REF 模式。外部可变数组通过显式的 local/global ref acquire 协议借用：`acquire_cached_shared_array_view<T>` 自持 cache 且不可复制或移动，第一次从自身或派生 subview 创建 holder 时 acquire 一次 global ref。cache 与所有依赖它的 borrowed view 必须同时存活；cache 释放自己的引用后，已创建的 holder 仍可独立保持缓冲区存活。

暂不新增 `ConstSharedArray<T>`。未来如需在 IDL 中表达只读共享数组，可以考虑独立的 `ConstSharedArray<T>`；但 C/C++ 层应复用 `SharedArray` 的句柄、生命周期和 C API，C++ 投影用 `shared_array<const T>` 表达只读元素访问。

## 6. 工程接入

### 6.1 代码生成映射

设计目标中的语义层内建泛型如下：

| IDL 名 | 语义类型 |
| --- | --- |
| `SharedVector` | `SharedVectorType` |
| `SharedSequence` | `SharedSequenceType` |
| `SharedMap` | `SharedMapType` |
| `SharedSet` | `SharedSetType` |
| `SharedArray` | `SharedArrayType` |

ABI 类型映射位于 `compiler/taihe/codegen/abi/analyses.py`，C++ 投影映射位于 `compiler/taihe/codegen/cpp/analyses.py`。ANI 后端的类型映射位于 `compiler/taihe/codegen/ani/analyses.py`，当前只支持从上层语言到 C++ 的容器代理生成。

#### ANI/ArkTS 投影

在 ANI 后端中，这些类型在 ArkTS 中的投影如下：

| IDL 类型 | TS 投影 | 说明 |
| --- | --- | --- | --- |
| `SharedSequence<T>` | `FixedArray<T>` | 将上层定长数组作为共享定长顺序容器代理。 |
| `SharedVector<T>` | `Array<T>` | 将上层可变数组作为共享顺序容器代理。 |
| `SharedMap<K, V>` | `Map<K, V>` | 将上层映射对象作为共享映射代理。 |
| `@record SharedMap<K, V>` | `Record<K, V>` | 使用 `@record` 时采用 Record 投影。 |
| `SharedSet<K>` | `Set<K>` | 将上层集合对象作为共享集合代理。 |
| `SharedArray<T>` | `ArrayBuffer` | 将上层 ArrayBuffer 作为共享连续内存封装。 |
| `@typedarray SharedArray<T>` | TypedArray | 同上，具体类型由元素标量类型决定。 |

#### ANI 传递限制

当前这七种投影类型在 ANI 后端只支持从上层语言传入 C++，而不支持从 C++ 传递到上层语言。虽然 `gen_into_ani` 仍会生成对应的转换入口，但实际运行时调用会直接抛出类似 `SharedContainer into_ani is not supported` 的运行时错误。这是有意保留的能力边界。

对于上层已有的 `Array`、`FixedArray`、`Map`、`Set`、`ArrayBuffer` 或 TypedArray，可以简单地通过 Taihe 接口机制被 C++ 侧保存为代理对象，因此，可以保证两侧的后续修改都将作用于同一个对象或同一段内存上。然而对于 C++ 侧创建的容器对象，由于 Taihe 的设计目标是作为一套“一次实现，多语言投影”的桥接模型，在 C++ 侧对象时，无法假定接收方是哪种语言的运行时，因而也不能直接创建特定上层语言的容器对象。 另一方面，ANI 没有提供从任意满足 `SharedVector`、`SharedSequence`、`SharedMap`、`SharedSet` 或 `SharedArray` 协议的对象创建上层语言容器的能力。所以在跨语言传递时，只能通过拷贝的方式将 C++ 侧的容器对象转换为上层语言的容器对象，然而这会破坏共享语义。因此，当前的选择是不支持从 C++ 传递到上层语言。

这条限制需要沿类型所在的数据结构和调用边界传递：

- 如果 `SharedVector`、`SharedSequence`、`SharedMap`、`SharedSet` 或 `SharedArray` 直接出现在结构体、联合体、普通数组或其它容器的成员/元素类型中，则包含它的整个数据类型都不支持从 C++ 传递到上层语言。
- 如果受限类型出现在接口、回调、接口化容器方法的返回值位置，则该方法不支持由 C++ 侧实现并被上层语言调用。
- 如果受限类型出现在接口、回调、接口化容器方法的参数位置，该方法不支持由 C++ 实现侧向上层语言发起调用。

因此，受限类型不仅限制自身的 C++ 到上层传递，也会限制所有直接或间接包含它的结构体、联合体、数组、容器、回调、接口方法和全局函数。后端后续如果增加双向支持，必须同时保证上层对象与 C++ 对象之间的共享身份、生命周期和可变性语义，而不能仅添加一次容器拷贝。

### 6.2 迁移与验证

旧 `Array`、`Vector`、`Map`、`Set` 保持不变；新类型逐步接入语义层、ABI 类型映射和 C++ 投影。

改动接口化容器时至少执行以下验证：

1. Python 语义层和 codegen 分析文件的语法检查。
2. 相关 runtime 头文件的 C++ `-fsyntax-only` 探针。
3. 涉及 `SharedArray` C API 时，编译 `runtime/src/shared_array.cpp`。
4. 接入具体后端投影后，补充对应后端的端到端容器传递测试。
