# Taihe ABI 内存布局文档

## 字符串类型

Taihe 字符串的 ABI 内存布局

```cpp
struct TString {
  uint32_t flags;
  uint32_t length;
  char const *ptr;  // always valid and non-null
};
```

```
+-------------+--------------+---------------------------+
| flags (u32) | length (u32) | ptr (char*, always valid) |
+-------------+--------------+---------------------------+
```

Author侧，即下层创建 Taihe 字符串时，会创建带有引用计数的 char* 字符串 TStringData

```cpp
struct TStringData {
  TRefCount count;
  char buffer[];
};
```

```
+---------------------+--------------------------+
| TRefCount count     | buffer[]                 |
+---------------------+--------------------------+
                      | 字符串内容（可变长度）   |
                      | 以 '\0' 作为结尾         |
```

注：下层创建的字符串 TString 的 ptr 指向 TStringData 的 buffer

## 定长数组（Array）

Taihe 数组类型的 ABI 内存布局

```cpp
struct TArray {
  size_t m_size;
  void *m_data;
};
```

```
+-----------------+----------------+
| m_size (size_t) | m_data (void*) |
+-----------------+----------------+
```

m_data里面存的是实际类型的指针，举例: 如果在 c++ 侧为 `taihe::array\<int64_t\>`，则 m_data 实际为 `int64_t*`

## optional

Taihe 可空类型的 ABI 内存布局

```c++
struct TOptional {
  void const *m_data;
};
```

```
+----------------+
| m_data (void*) |
+----------------+
```

同上，m_data里面存的是实际类型的指针

## vector

## set

Taihe 的 set 类型使用 **Separate Chaining** 实现

```cpp
template<typename K>
struct set_view {
    using item_t = K const;

    struct node_t {
        item_t item;
        node_t *next;
    };

private:
    struct handle_t {
        TRefCount count;
        std::size_t cap;
        node_t **bucket;
        std::size_t size;
    } *m_handle;
};
```

```
      set_view<K>
┌─────────────────────┐
│   m_handle ───────┐ │
└───────────────────│─┘
                    │
                 handle_t
          ┌──────────────────────┐
          │   TRefCount count    │
          │   std::size_t cap    │
          │   node_t** bucket ──────┐
          │   std::size_t size   │  │
          └──────────────────────┘  │
                                    │
                           node_t* bucket[0..cap-1]
                    ┌───────────────┬────────────────────────────────────┐
                    │   bucket[0]   │ node_t --> node_t --> ... --> NULL │
                    │   bucket[1]   │ NULL                               │
                    │     ...       │ ...                                │
                    │ bucket[cap-1] │ node_t --> NULL                    │
                    └───────────────┴────────────────────────────────────┘
```

## map

Taihe 的 map 类型与 set 类型同理

```cpp
template<typename K, typename V>
struct map_view {
public:
    using item_t = std::pair<K const, V>;

    struct node_t {
        item_t item;
        node_t *next;
    };

private:
    struct handle_t {
        TRefCount count;
        std::size_t cap;
        node_t **bucket;
        std::size_t size;
    } *m_handle;
};
```

## struct

taihe 的 struct 是值类型的 struct

```rust
struct Color {
    R: i32;
    G: i32;
    B: i32;
}
```

```cpp
struct binding_Color_t {
    int32_t R;
    int32_t G;
    int32_t B;
};
```

注：此处 binding 为 package_name

## enum

```rust
enum MessageType: i32 {
    Text = 1,
    Number = 2,
}

enum EnumString: String {
    ONE = "hello",
    TWO = "world",
    THREE = "good morning"
}
```

c++侧会生成：

```cpp
struct MessageType {
public:
    enum class key_t: int {
        Text,
        Number,
    };

    static constexpr int32_t table[] = {
        1,
        2,
    };

    // ...

private:
    key_t key;
};

struct EnumString {
public:
    enum class key_t: int {
        ONE,
        TWO,
        THREE,
    };

    static constexpr char const* table[] = {
        "hello",
        "world",
        "good morning",
    };

    // ...

private:
    key_t key;
};
```

所以，Taihe enum 的实际内存为 int, 对应的值存储在常量列表中

## union

```rust
union MessageData {
    textVal: String;
    numVal: i64;
}
```

```cpp
union message_MessageData_union {
    struct TString textVal;
    int64_t numVal;
};
struct message_MessageData_t {
    int m_tag;
    union message_MessageData_union m_data;
};
```

`union message_MessageData_union` 的实际内存大小是其所有成员中最大成员的大小

Taihe union 实际内存布局即`struct message_MessageData_t`

union 实际是 enum 的延申

## interface

参考 [Interface ABI文档](./InterfaceAbi.md)

## callback

Taihe 的 callback 是本质上是 Taihe 的 interface

```cpp
struct TCallback {
  void *vtbl_ptr;                // 指向函数实现
  struct DataBlockHead *data_ptr; // 指向闭包数据
};
```
