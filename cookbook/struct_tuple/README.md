# Struct 与 Tuple

> **学习目标**：掌握 Taihe 中 `struct` 的基本定义与使用，以及 `@tuple` 注解将 struct 投影为元组类型。

## 核心概念

### Struct

Taihe 的 `struct` 是纯数据类型，用于在 ArkTS 和 C++ 之间传递结构化数据。无需用户编写实现代码，Taihe 会自动生成两端的转换逻辑。

在 ArkTS 侧，struct 默认投影为 `interface`（或使用 `@class` 投影为 `class`），通过**属性名**访问字段。

### @tuple

使用 `@tuple` 注解后，struct 在 ArkTS 侧投影为**元组类型**，通过**下标**访问字段。

| 对比项 | 普通 struct | `@tuple` struct |
|--------|-------------|-----------------|
| ArkTS 类型 | `interface` / `class` | 元组 `[T0, T1, ...]` |
| 访问方式 | `obj.fieldName` | `obj[0]`, `obj[1]`, ... |
| 构造方式 | `{ field: value }` | `[value0, value1]` |
| C++ 侧 | 命名字段 struct | 命名字段 struct（不变） |

> **注意**：`@tuple` 只影响 ArkTS 侧的投影方式，C++ 侧仍然使用命名字段访问（如 `p.x`、`p.y`）。

---

## 第一步：定义接口

**File: `idl/struct_tuple.taihe`**

```rust
// 基础 struct
struct Color {
    r: i32;
    g: i32;
    b: i32;
}

function makeColor(r: i32, g: i32, b: i32): Color;
function mixColors(a: Color, b: Color): Color;

// @tuple struct
@tuple
struct Point {
    x: f64;
    y: f64;
}

@tuple
struct NamedPoint {
    name: String;
    x: f64;
    y: f64;
}

function makePoint(x: f64, y: f64): Point;
function distance(a: Point, b: Point): f64;
function makeNamedPoint(name: String, x: f64, y: f64): NamedPoint;
function describePoint(p: NamedPoint): String;

// @tuple 嵌套与数组
@tuple
struct Segment {
    start: Point;
    end: Point;
}

function makeSegment(x1: f64, y1: f64, x2: f64, y2: f64): Segment;
function segmentLength(seg: Segment): f64;
function makePointArray(n: i32): Array<Point>;
```

### 生成的 ArkTS 类型

普通 struct 生成 interface：

```typescript
export interface Color {
    r: int;
    g: int;
    b: int;
}
```

`@tuple` struct 生成元组类型：

```typescript
export type Point = [number, number];
export type NamedPoint = [string, number, number];
export type Segment = [Point, Point];  // 即 [[number, number], [number, number]]
```

## 第二步：实现 C++ 代码

**File: `author/src/struct_tuple.impl.cpp`**

```cpp
#include "struct_tuple.impl.hpp"
#include "struct_tuple.proj.hpp"

#include <cmath>
#include <sstream>

using namespace taihe;
using namespace struct_tuple;

// 基础 struct：使用聚合初始化
Color makeColor(int32_t r, int32_t g, int32_t b) {
    return {r, g, b};
}

Color mixColors(Color const &a, Color const &b) {
    return {(a.r + b.r) / 2, (a.g + b.g) / 2, (a.b + b.b) / 2};
}

// @tuple struct：C++ 侧与普通 struct 完全一致
Point makePoint(double x, double y) {
    return {x, y};
}

double distance(Point const &a, Point const &b) {
    double dx = a.x - b.x;
    double dy = a.y - b.y;
    return std::sqrt(dx * dx + dy * dy);
}

NamedPoint makeNamedPoint(string_view name, double x, double y) {
    return {name, x, y};
}

taihe::string describePoint(NamedPoint const &p) {
    std::ostringstream oss;
    oss << std::string(p.name.data(), p.name.size())
        << "(" << p.x << ", " << p.y << ")";
    return taihe::string(oss.str());
}

// @tuple 嵌套：使用嵌套聚合初始化
Segment makeSegment(double x1, double y1, double x2, double y2) {
    return {{x1, y1}, {x2, y2}};
}

double segmentLength(Segment const &seg) {
    double dx = seg.end.x - seg.start.x;
    double dy = seg.end.y - seg.start.y;
    return std::sqrt(dx * dx + dy * dy);
}

// Array<@tuple>
taihe::array<Point> makePointArray(int32_t n) {
    taihe::array<Point> arr(n);
    for (int32_t i = 0; i < n; i++) {
        arr[i] = {static_cast<double>(i), static_cast<double>(i * i)};
    }
    return arr;
}

TH_EXPORT_CPP_API_makeColor(makeColor);
TH_EXPORT_CPP_API_mixColors(mixColors);
TH_EXPORT_CPP_API_makePoint(makePoint);
TH_EXPORT_CPP_API_distance(distance);
TH_EXPORT_CPP_API_makeNamedPoint(makeNamedPoint);
TH_EXPORT_CPP_API_describePoint(describePoint);
TH_EXPORT_CPP_API_makeSegment(makeSegment);
TH_EXPORT_CPP_API_segmentLength(segmentLength);
TH_EXPORT_CPP_API_makePointArray(makePointArray);
```

> **注意**：在 C++ 侧，`@tuple` struct 和普通 struct 的使用方式完全一致，都通过字段名访问。

## 第三步：编译运行

```sh
taihe-tryit test -u ani cookbook/struct_tuple
```

## 使用示例

**File: `user/main.ets`**

```typescript
import * as st from "struct_tuple";

loadLibrary("struct_tuple");

function main() {
    // ===== 基础 struct：通过属性名访问字段 =====
    let red = st.makeColor(255, 0, 0);
    let blue = st.makeColor(0, 0, 255);
    console.log("red: r=" + red.r + " g=" + red.g + " b=" + red.b);

    let purple = st.mixColors(red, blue);
    console.log("purple: r=" + purple.r + " g=" + purple.g + " b=" + purple.b);

    // ===== @tuple struct：通过下标访问字段 =====
    let p1 = st.makePoint(0.0, 0.0);
    let p2 = st.makePoint(3.0, 4.0);
    console.log("p1: [" + p1[0] + ", " + p1[1] + "]");
    console.log("p2: [" + p2[0] + ", " + p2[1] + "]");
    console.log("distance: " + st.distance(p1, p2));

    // @tuple 可以用字面量构造
    let p3: st.Point = [1.0, 1.0];
    console.log("distance p2-p3: " + st.distance(p2, p3));

    // ===== @tuple 嵌套 =====
    let seg = st.makeSegment(0.0, 0.0, 3.0, 4.0);
    console.log("start: [" + seg[0][0] + ", " + seg[0][1] + "]");
    console.log("end: [" + seg[1][0] + ", " + seg[1][1] + "]");
    console.log("length: " + st.segmentLength(seg));

    // ===== Array<@tuple> =====
    let points = st.makePointArray(4);
    for (let i = 0; i < points.length; i++) {
        console.log("points[" + i + "]: [" + points[i][0] + ", " + points[i][1] + "]");
    }
}
```

**输出：**

```
red: r=255 g=0 b=0
purple: r=127 g=0 b=127
p1: [0, 0]
p2: [3, 4]
distance: 5
distance p2-p3: 3.605551275463989
name: origin x: 0 y: 0
origin(0, 0)
start: [0, 0]
end: [3, 4]
length: 5
points[0]: [0, 0]
points[1]: [1, 1]
points[2]: [2, 4]
points[3]: [3, 9]
```

---

## 相关文档

- [Struct 继承](../struct_extends/README.md) - 使用 `@extends` 实现 struct 组合式继承
- [属性](../property/README.md) - `@readonly` 只读字段
- [Optional](../optional/README.md) - 可选字段与可空类型
