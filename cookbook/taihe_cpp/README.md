# Taihe C++ 使用指南

## string

1. string 使用引用计数进行自动的生命周期管理, 用户只需要正常使用 string

2. 为方便用户使用，提供了许多相关的操作函数便于用户开发

```C++
// 使用字符串创建 taihe::string
taihe::string s1("Hello");

// 使用字符串与长度创建 taihe::string
taihe::string s2("World", 5);

// 使用 std::string 创建 taihe::string
taihe::string s3(std::string_view("C++"));
taihe::string s4(std::string("Example"));

// 使用 taihe::string 创建 std::string_view
std::string_view(s3);
std::string(s3);

// string 可以使用 << 输出
std::cout << "s1: " << s1 << "\n";

// 使用已有字符串为 string_view 进行 0 拷贝的初始化
taihe::string_view sv1 = s1;

// string_view 可以使用 << 输出
std::cout << "sv1: " << sv1 << "\n";

// 访问字符串首字符和尾字符
std::cout << "s1 front: " << s1.front() << "\n";
std::cout << "s1 back: " << s1.back() << "\n";

// 连接字符串
taihe::string s5 = s1 + s2;
std::cout << "s1 + s2: " << s5 << "\n";

// 截取子字符串
taihe::string s6 = s5.substr(0, 5); // arg0: begin position, arg1: len
std::cout << "Substring of s5 (first 5 chars): " << s6 << "\n";

// 比较字符串
std::cout << std::boolalpha;
std::cout << "s1 == s2: " << (s1 == s2) << "\n";

// 转换整数到 taihe::string
taihe::string numStr = to_string(12345);
std::cout << "to_string(12345): " << numStr << "\n";

// 转换浮点数到 taihe::string
taihe::string floatStr = to_string(3.1415);
std::cout << "to_string(3.1415): " << floatStr << "\n";

// 转换布尔值到 taihe::string
taihe::string boolTrueStr = to_string(true);
taihe::string boolFalseStr = to_string(false);
std::cout << "to_string(true): " << boolTrueStr << "\n";
std::cout << "to_string(false): " << boolFalseStr << "\n";
```

## array

```C++
// 使用初始化列表方式创建taihe::array
taihe::array<int> arr = {10, 20, 30, 40, 50}

// 通过 std::vector 创建 taihe::array_view
std::vector<double> vec = {3.14, 2.71, 1.62};
taihe::array_view<double> view(vec);

// 使用std::vector 创建 taihe::array
std::vector<int> vec = {1, 2, 3};
taihe::array<int> arr1(taihe::array_view<T>(vec));

// 通过索引访问 taihe::array 内的元素
std::cout << "Using operator[]: " << view[2] << "\n";
// 通过 at() 访问 taihe::array 内的元素
std::cout << "Using at(): " << view.at(1) << "\n";
// 访问首元素
std::cout << "Front: " << view.front() << "\n";
// 访问尾元素
std::cout << "Back: " << view.back() << "\n";
// 获取数组大小
std::cout << "Size: " << view.size() << "\n";

// 注意使用 begin()、end()、rbegin()、rend() 获取的是指针
// 遍历
std::cout << "Iterating using begin() and end(): ";
for (auto it = arr.begin(); it != arr.end(); ++it) {
    std::cout << *it << " ";
}
std::cout << "\n";

// 反向遍历
std::cout << "Iterating using rbegin() and rend(): ";
for (auto it = arr.rbegin(); it != arr.rend(); ++it) {
    std::cout << *it << " ";
}
```

## set

```C++
// 创建 taihe::set
taihe::set<taihe::string> my_set;

// 创建具体容量的 taihe::set，会自动动态扩容
taihe::set<taihe::string> s1(10);

// 插入元素 emplace()
my_set.emplace("apple");
my_set.emplace("banana");
my_set.emplace("cherry");

// 查找元素 find_item()
if (my_set.find_item("banana")) {
    std::cout << "banana found" << std::endl;
}

// 删除元素 erase()
my_set.erase("apple");

// 遍历元素
for (auto const &key : my_set) {
    std::cout << "  " << key << std::endl;
}

// 使用 empty() 判断 set 是否为空，使用 size() 获取元素个数
if (!my_set.empty()) {
    std::cout << "set size = " << my_set.size() << std::endl;
}

// 使用 capacity() 判断容量
std::cout << "set capacity = " << my_set.capacity() << std::endl;

// 清空元素 claer()
my_set.clear();
```

## map

```C++
// 创建一个空 taihe::map
taihe::map<taihe::string, int32_t> my_map;

// 插入元素 emplace(key, value)
my_map.emplace("apple", 5);
my_map.emplace("banana", 3);
my_map.emplace("orange", 10);

// 查找元素 find_item()
// 之前的 find() 方法已弃用，用户请不要使用 find() 方法, 而是使用目前的 find_item() 方法
if (auto* result = my_map.find_item("apple")) {
    std::cout << "Found: key = " << result->first << ", value = " << result->second << "\n";
} else {
    std::cout << "Key 'apple' not found.\n";
}

// 修改元素 emplace<true>(key, value)
my_map.emplace<true>("orange", 6);

// 遍历所有元素
for (auto [key, val] : my_map) {
    std::cout << "- " << key << ": " << val << std::endl;
}

// 删除元素 erase()
if (my_map.erase("apple")) {
    std::cout << "apple removed\n";
}

// 访问 taihe::map 所有元素的 lambda 回调遍历函数 accept()
my_map.accept([](const std::string& k, int32_t v) {
    std::cout << "- " << k << ": " << v << std::endl;
});

// 获取 taihe::map 当前大小 size()
std::cout << "Map size: " << my_map.size() << std::endl;

// 获取 taihe::map 当前容量 capacity()
std::cout << "Map capacity: " << my_map.capacity() << std::endl;

// 当前taihe::map 是否为空
std::cout << "Map is empty: " << std::boolalpha << my_map.empty() << std::endl;
```

## optional

```C++
// 创建空Optional
optional<T>(std::nullopt);
// 创建非空Optional
optional<T>(std::in_place_t{}, val);

optional<int32_t> opt_var = optional<int32_t>(std::in_place_t{}, 1);
// 判断Optional是否为空
bool tag = bool(opt_var);

bool tag = opt_var.has_value();

// 获取Optional值
int32_t var0 = *opt_var;
int32_t var1 = opt_var.value();
```

## enum

```taihe
enum MessageType: i32 {
    Text = 1,
    Number = 2,
}
```

```C++
// 创建enum
MessageType enum_var1 = MessageType::key_t::Text;
MessageType enum_var2 = MessageType::key_t::Number;

// 获取键与值 get_key() 与 get_val()
if (enum_var1.get_key() == MessageType::key_t::Text) {
    std::cout << "enum key is Text" << std::cout;
}

std::cout << enum_var1.get_value() << std::cout;
// output: 1
```

## union

```taihe
union MessageData {
    textVal: String;
    numVal: i64;
}
```

```C++
// 创建 union 使用 {union_type}::make_{item}({value});
MessageData msg_data = MessageData::make_textVal("hello");

// 获取 union 值使用 get_{item}_ref()
std::cout << "text: " << msg_data.get_textVal_ref() << std::endl;
```

## struct

```taihe
struct Color{
    R: i32;
    G: i32;
    B: i32;
}
```

```C++
// C++ 侧创建 taihe 结构体使用大括号初始化
Color white{255, 255, 255};

// 读取结构体内的属性值
std::cout << "R = " << white.R << "G = " << white.G << "B = " << white.B << std::endl;
```

## interface

```taihe
interface Base {
    foo(): void;
}

interface Derived : Base {
    bar(): void;
}

function makeBase(): Base;
function makeDerived(a: i32): Derived;
```

```C++
// 类实现
class BaseImpl {
public:
    BaseImpl() {}

    void foo() {
        std::cout << "Base Foo Method" << std::endl;
    }
};

class DerivedImpl {
public:
    DerivedImpl() {
        this->m_var = 0;
    }

    DerivedImpl(int32_t a): m_var(a) {}

    void bar() {
        std::cout << "Derived Bar Method" <<  << std::endl;
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

C++ 侧使用类

```C++
// 创建类
Base baseObj = taihe::make_holder<BaseImpl, Base>();
Derived derivedOBj = taihe::make_holder<DerivedImpl, Derived>(1);

// 得到weak类型类对象
weak::Base weakBaseObj = baseObj;

// weak 类型转换为非 weak 类型
Base baseObj2 = Base(weakBaseObj);

// 子类转换为父类，静态转换
Base newDerivedOBj = Base(derivedOBj);

// 父类转换为子类，动态转换
Derived newDerivedOBj2 = Derived(newDerivedOBj);

// 调用函数 ->
baseObj->foo();
derivedOBj->foo(); // X 不允许子类直接调用父类函数，需要先转换为父类
derivedOBj->bar();
```