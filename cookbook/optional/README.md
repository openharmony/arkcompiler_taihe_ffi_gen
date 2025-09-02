# optional

本章节介绍 `Optional` 与 `Record`

taihe `Optional<T>` 在 ets 中对应 `T | undefined`，如 `optional<String>` 对应 `string | undefined`

taihe 使用给 `Map` 增加注解的方式，支持 ets 中的 `Record`

下面以 用户设置 场景为例进行介绍

## 第一步：编写接口原型

**File: `idl/userSettings.taihe`**

```rust
function getUserSetting(settings: @record Map<String, String>, key: String): Optional<String>;
```

该函数用于根据 key 查找用户设置，返回一个 `Optional<String>` 类型

`@record` 注解的使用方法为增加在 Map 类型前面，这样在 sts 侧会对应 `Record` 类型

## 第二步：完成 C++ 实现

**File: `author/src/userSettings.impl.cpp`**

```cpp
optional<string> getUserSetting(map_view<string, string> settings, string_view key) {
    auto iter = settings.find_item(key);
    if (iter == nullptr) {
        return optional<string>(std::nullopt);
    }
    return optional<string>(std::in_place, iter->second);
}
```

这里对 C++ 实现中的 optional 与 map 进行介绍

1. `taihe::optional<T>`

    - 创建空 optional

        创建空 opional 的方法如下，其中 T 改为对应类型

        ```cpp
        optional<T>(std::nullopt);
        ```

    - 创建非空 optional

        创建非空 optional 的方法如下，其中 T 改为对应类型，val 使用对应类型的变量

        ```cpp
        optional<T>(std::in_place, val);
        ```

2. `taihe::map<K, V>`

    - `find_item()`

        使用 `find_item()` 函数可以查找 key 对应的 value，查找成功时，返回 `std::pair<K, V>` 类型的指针，查找失败时，返回 `nullptr`

    - 遍历

        可以使用如下方法对 map 进行遍历

        ```cpp
        for (auto it = settings.begin(); it != settings.end(); ++it) {
            std::cout << "Key: " << it->first << ", Value: " << it->second << std::endl;
        }
    
        for (auto const& [key, value] : settings) {
            std::cout << "Key: " << key << ", Value: " << value << std::endl;
        }
        ```

另外需要注意的时，生成 temp 文件夹下，使用了 `using namespace userSettings;`，如果直接编译会编译不通过，因为该样例没有任何对象，所以没有 include 这个命名空间，如果在 Taihe IDL 文件没有使用对象的场景下，需要手动将该语句删除

希望读者明白生成的 temp 文件夹下的文件是用于作为参考，而非让使用者直接作为模板套用

## 第三步：在 ets 侧使用

**File: `user/main.ets`**

```typescript
// 初始化 Record
let Settings: Record<string, string> = {
    "theme": "dark",
    "fontSize": "14px",
    "language": "en-US",
};
// 查找设置
let setting1 = userSettings.getUserSetting(Settings, "theme");
let setting2 = userSettings.getUserSetting(Settings, "autosave");
console.log("theme: " + setting1);
console.log("autosave: " + setting2);
```

**Stdout**

```sh
theme: dark
autosave: undefined
```

## Optional 补充

```cpp
// 创建 Optional

// 创建空 Optional
optional<T>(std::nullopt);
// 创建非空 Optional
optional<T>(std::in_place, val);

optional<int32_t> opt_var = optional<int32_t>(std::in_place, 1);
// 判断 Optional 是否为空
bool tag = bool(opt_var);

bool tag = opt_var.has_value();

// 获取 Optional 值
int32_t var0 = *opt_var;
int32_t var1 = opt_var.value();
```
