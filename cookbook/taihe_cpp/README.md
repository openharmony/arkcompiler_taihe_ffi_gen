# Taihe C++ API 参考

> **学习目标**：掌握 Taihe 在 C++ 侧提供的各种类型和 API。

## String

Taihe 提供 `taihe::string` 和 `taihe::string_view` 类型，使用引用计数自动管理生命周期。

```cpp
// 创建
taihe::string s1("Hello");
taihe::string s2("World", 5);  // 指定长度
taihe::string s3(std::string_view("C++"));
taihe::string s4(std::string("Example"));

// 转换为 std::string
std::string_view(s3);
std::string(s3);

// 创建 string_view（零拷贝）
taihe::string_view sv1 = s1;

// 输出
std::cout << s1 << std::endl;

// 访问字符
std::cout << s1.front() << std::endl;  // 首字符
std::cout << s1.back() << std::endl;   // 尾字符

// 连接
taihe::string s5 = s1 + s2;

// 截取子串
taihe::string s6 = s5.substr(0, 5);  // (起始位置, 长度)

// 比较
bool eq = (s1 == s2);

// 类型转换
taihe::string numStr = to_string(12345);
taihe::string floatStr = to_string(3.1415);
taihe::string boolStr = to_string(true);
```

---

## Array

```cpp
// 使用初始化列表创建
taihe::array<int> arr = {10, 20, 30, 40, 50};

// 从 std::vector 创建
std::vector<int> vec = {1, 2, 3};
taihe::array<int> arr1(taihe::array_view<int>(vec));

// 创建 array_view
taihe::array_view<int> view(vec);

// 访问元素
view[2];           // 索引访问
view.at(1);        // at() 访问
view.front();      // 首元素
view.back();       // 尾元素
view.size();       // 大小

// 遍历
for (auto it = arr.begin(); it != arr.end(); ++it) {
    std::cout << *it << " ";
}

// 反向遍历
for (auto it = arr.rbegin(); it != arr.rend(); ++it) {
    std::cout << *it << " ";
}
```

---

## Set

```cpp
// 创建
taihe::set<taihe::string> my_set;
taihe::set<taihe::string> s1(10);  // 指定初始容量

// 插入
my_set.emplace("apple");
my_set.emplace("banana");

// 查找
if (my_set.find_item("banana")) {
    std::cout << "found" << std::endl;
}

// 删除
my_set.erase("apple");

// 遍历
for (auto const& key : my_set) {
    std::cout << key << std::endl;
}

// 属性
my_set.empty();     // 是否为空
my_set.size();      // 元素个数
my_set.capacity();  // 容量
my_set.clear();     // 清空
```

---

## Map

```cpp
// 创建
taihe::map<taihe::string, int32_t> my_map;

// 插入
my_map.emplace("apple", 5);
my_map.emplace("banana", 3);

// 查找（使用 find_item，find 已废弃）
if (auto* result = my_map.find_item("apple")) {
    std::cout << result->first << ": " << result->second << std::endl;
}

// 修改（使用 emplace<true>）
my_map.emplace<true>("apple", 10);

// 遍历
for (auto [key, val] : my_map) {
    std::cout << key << ": " << val << std::endl;
}

// 删除
my_map.erase("apple");

// 属性
my_map.size();
my_map.capacity();
my_map.empty();
```

---

## Optional

```cpp
// 创建空值
optional<int> empty = std::nullopt;

// 创建有值
optional<int> value{std::in_place, 42};

// 判断是否有值
if (value.has_value()) { ... }
if (bool(value)) { ... }

// 获取值
int val = *value;
int val = value.value();
```

---

## Enum

**Taihe IDL:**

```rust
enum MessageType: i32 {
    Text = 1;
    Number = 2;
}
```

**C++ 使用:**

```cpp
// 创建
MessageType type = MessageType::key_t::Text;

// 获取键和值
MessageType::key_t key = type.get_key();
int32_t val = type.get_value();

// switch 判断
switch (type.get_key()) {
    case MessageType::key_t::Text:
        break;
    case MessageType::key_t::Number:
        break;
}
```

---

## Union

**Taihe IDL:**

```rust
union MessageData {
    textVal: String;
    numVal: i64;
}
```

**C++ 使用:**

```cpp
// 创建
MessageData data = MessageData::make_textVal("hello");

// 获取标签
MessageData::tag_t tag = data.get_tag();

// switch 判断
switch (data.get_tag()) {
    case MessageData::tag_t::textVal:
        std::cout << data.get_textVal_ref() << std::endl;
        break;
    case MessageData::tag_t::numVal:
        std::cout << data.get_numVal_ref() << std::endl;
        break;
}
```

---

## Struct

**Taihe IDL:**

```rust
struct Color {
    R: i32;
    G: i32;
    B: i32;
}
```

**C++ 使用:**

```cpp
// 创建（大括号初始化）
Color white{255, 255, 255};

// 访问属性
std::cout << white.R << white.G << white.B << std::endl;
```

---

## Interface

**Taihe IDL:**

```rust
interface Base {
    foo(): void;
}

interface Derived : Base {
    bar(): void;
}

function makeBase(): Base;
function makeDerived(a: i32): Derived;
```

**C++ 实现:**

```cpp
class BaseImpl {
public:
    void foo() {
        std::cout << "Base Foo" << std::endl;
    }
};

class DerivedImpl {
public:
    DerivedImpl(int32_t a) : m_var(a) {}

    void bar() {
        std::cout << "Derived Bar" << std::endl;
    }

    void foo() {
        TH_THROW(std::runtime_error, "foo not implemented");
    }

private:
    int32_t m_var;
};

Base makeBase() {
    return taihe::make_holder<BaseImpl, Base>();
}

Derived makeDerived(int32_t a) {
    return taihe::make_holder<DerivedImpl, Derived>(a);
}
```

**C++ 使用:**

```cpp
// 创建
Base baseObj = taihe::make_holder<BaseImpl, Base>();
Derived derivedObj = taihe::make_holder<DerivedImpl, Derived>(1);

// 转换为 weak 类型
weak::Base weakBase = baseObj;

// weak 转非 weak
Base baseObj2 = Base(weakBase);

// 子类转父类（静态）
Base asBase = Base(derivedObj);

// 父类转子类（动态）
Derived asDerived = Derived(asBase);

// 调用方法
baseObj->foo();
derivedObj->bar();
// 注意：子类不能直接调用父类方法，需先转换为父类
```

---

## Callback

```cpp
// callback 作为参数时为 callback_view 类型（不具备所有权）
void foo(callback_view<string(int32_t)> cb) {
    // 如果需要保存，需转换为 callback 类型
    callback<string(int32_t)> saved(cb);
    
    // 调用
    string result = cb(42);
}
```

---

## 相关文档

- [基础类型](../basic_abilities/README.md) - 类型映射表
- [Enum 与 Union](../enum_union/README.md) - 详细示例
- [Interface 接口](../interface/README.md) - 接口使用
