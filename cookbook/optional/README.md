# Optional 与 Record

> **学习目标**：掌握 Taihe 中可选类型（Optional）、`@optional` 注解和 Record 类型的使用。

本教程介绍 `Optional` 类型、`@optional` 注解与 `@record` 的用法。

## 核心概念

| Taihe 类型/注解 | ArkTS 类型 | 说明 |
|-----------------|------------|------|
| `Optional<T>` | `T \| undefined` | 可选值，可能为空 |
| `@optional field: Optional<T>` | `field?: T` | **可选属性/参数**（更常用） |
| `@record Map<K, V>` | `Record<K, V>` | 键值对集合 |

> **重要**：`@optional` 注解用于将参数或属性标记为可选（`?:`），这是 ArkTS API 中最常用的场景。注意类型本身仍需为 `Optional<T>`。

---

## @optional 注解（推荐用法）

`@optional` 注解可以加在 **struct 字段** 或 **函数参数** 上，使其在 ArkTS 侧生成可选属性/参数。

### Struct 可选字段

**File: `idl/image.taihe`**

```rust
struct DecodingOptions {
    @optional index: Optional<i32>;           // index?: int
    @optional sampleSize: Optional<i32>;      // sampleSize?: int
    @optional editable: Optional<bool>;       // editable?: boolean
    @optional desiredSize: Optional<Size>;    // desiredSize?: Size
}
```

**生成的 ArkTS 代码：**

```typescript
export interface DecodingOptions {
    index?: int;
    sampleSize?: int;
    editable?: boolean;
    desiredSize?: Size;
}
```

**ArkTS 使用示例：**

```typescript
// 所有字段都是可选的
let options1: DecodingOptions = {};
let options2: DecodingOptions = { index: 0 };
let options3: DecodingOptions = { index: 0, sampleSize: 2, editable: true };
```

### 函数可选参数

**File: `idl/api.taihe`**

```rust
function createPixelMap(@optional options: Optional<DecodingOptions>): PixelMap;
function getImageInfo(@optional index: Optional<i32>): ImageInfo;
```

**生成的 ArkTS 代码：**

```typescript
export function createPixelMap(options?: DecodingOptions): PixelMap;
export function getImageInfo(index?: int): ImageInfo;
```

**ArkTS 使用示例：**

```typescript
// 可以不传可选参数
let pixelMap1 = createPixelMap();
let pixelMap2 = createPixelMap({ index: 0 });

let info1 = getImageInfo();
let info2 = getImageInfo(0);
```

### C++ 侧实现

在 C++ 侧，`@optional` 字段/参数类型仍然是 `optional<T>`：

```cpp
PixelMap createPixelMap(optional<DecodingOptions> options) {
    if (options.has_value()) {
        // 使用 options.value() 获取配置
        auto& opts = options.value();
        // ...
    } else {
        // 使用默认配置
    }
    return make_pixel_map();
}

TH_EXPORT_CPP_API_createPixelMap(createPixelMap);
```

---

## Optional 类型（基础用法）

不使用 `@optional` 注解时，`Optional<T>` 映射为 `T | undefined`：

**File: `idl/userSettings.taihe`**

```rust
function getUserSetting(
    settings: @record Map<String, String>, 
    key: String
): Optional<String>;
```

- 返回 `Optional<String>` 表示可能找不到对应的设置项
- `@record` 注解使 `Map` 在 ArkTS 侧映射为 `Record` 类型

## C++ 实现

**File: `author/src/userSettings.impl.cpp`**

```cpp
#include "userSettings.impl.hpp"

using namespace taihe;

optional<string> getUserSetting(map_view<string, string> settings, string_view key) {
    auto iter = settings.find_item(key);
    if (iter == nullptr) {
        return optional<string>(std::nullopt);  // 返回空值
    }
    return optional<string>(std::in_place, iter->second);  // 返回找到的值
}

TH_EXPORT_CPP_API_getUserSetting(getUserSetting);
```

### C++ API 参考

#### Optional 操作

| 操作 | 语法 | 示例 |
|------|------|------|
| 创建空值 | `optional<T>(std::nullopt)` | `optional<string>(std::nullopt)` |
| 创建有值 | `optional<T>(std::in_place, val)` | `optional<string>(std::in_place, "hello")` |
| 判断是否有值 | `.has_value()` 或 `bool(opt)` | `if (opt.has_value())` |
| 获取值 | `.value()` 或 `*opt` | `string s = opt.value();` |

#### Map 操作

| 操作 | 语法 | 说明 |
|------|------|------|
| 查找元素 | `map.find_item(key)` | 返回 `std::pair<K,V>*`，未找到返回 `nullptr` |
| 遍历 | `for (auto& [k, v] : map)` | 支持范围 for 循环 |

**遍历示例：**

```cpp
for (auto const& [key, value] : settings) {
    std::cout << key << ": " << value << std::endl;
}
```

## 编译运行

```sh
taihe-tryit test -u sts cookbook/userSettings
```

## 使用示例

**File: `user/main.ets`**

```typescript
import * as userSettings from "userSettings";

loadLibrary("userSettings");

function main() {
    // 初始化设置
    let settings: Record<string, string> = {
        "theme": "dark",
        "fontSize": "14px",
        "language": "en-US"
    };
    
    // 查找存在的设置
    let theme = userSettings.getUserSetting(settings, "theme");
    console.log("theme: " + theme);  // theme: dark
    
    // 查找不存在的设置
    let autosave = userSettings.getUserSetting(settings, "autosave");
    console.log("autosave: " + autosave);  // autosave: undefined
}
```

**输出：**

```
theme: dark
autosave: undefined
```

---

## Optional 完整示例

```cpp
// 创建 Optional
optional<int32_t> empty_opt(std::nullopt);           // 空值
optional<int32_t> value_opt(std::in_place, 42);      // 有值

// 判断是否有值
if (value_opt.has_value()) {
    // 获取值
    int32_t val = value_opt.value();  // 或 *value_opt
}

// 使用 bool 转换判断
if (bool(value_opt)) {
    std::cout << "has value" << std::endl;
}
```

---

## 相关文档

- [Enum 与 Union](../enum_union/README.md) - 枚举和联合类型
- [基础类型](../basic_abilities/README.md) - 基本类型映射
