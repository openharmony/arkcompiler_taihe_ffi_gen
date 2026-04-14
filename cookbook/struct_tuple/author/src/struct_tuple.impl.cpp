/*
 * Copyright (c) 2025 Huawei Device Co., Ltd.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// This file is a test file.
// NOLINTBEGIN
#include "struct_tuple.impl.hpp"
#include "struct_tuple.proj.hpp"

#include <cmath>
#include <sstream>
#include <string>

using namespace taihe;
using namespace struct_tuple;

namespace {

// ===== 基础 struct =====

::taihe::expected<Color, ::taihe::error> makeColor(int32_t r, int32_t g, int32_t b)
{
    return Color {r, g, b};
}

::taihe::expected<Color, ::taihe::error> mixColors(Color const &a, Color const &b)
{
    return Color {(a.r + b.r) / 2, (a.g + b.g) / 2, (a.b + b.b) / 2};
}

// ===== @tuple struct =====

::taihe::expected<Point, ::taihe::error> makePoint(double x, double y)
{
    return Point {x, y};
}

::taihe::expected<double, ::taihe::error> distance(Point const &a, Point const &b)
{
    double dx = a.x - b.x;
    double dy = a.y - b.y;
    return std::sqrt(dx * dx + dy * dy);
}

::taihe::expected<NamedPoint, ::taihe::error> makeNamedPoint(string_view name, double x, double y)
{
    return NamedPoint {name, x, y};
}

::taihe::expected<taihe::string, ::taihe::error> describePoint(NamedPoint const &p)
{
    std::ostringstream oss;
    oss << std::string(p.name.data(), p.name.size()) << "(" << p.x << ", " << p.y << ")";
    return taihe::string(oss.str());
}

// ===== @tuple 嵌套与数组 =====

::taihe::expected<Segment, ::taihe::error> makeSegment(double x1, double y1, double x2, double y2)
{
    return Segment {{x1, y1}, {x2, y2}};
}

::taihe::expected<double, ::taihe::error> segmentLength(Segment const &seg)
{
    double dx = seg.end.x - seg.start.x;
    double dy = seg.end.y - seg.start.y;
    return std::sqrt(dx * dx + dy * dy);
}

::taihe::expected<taihe::array<Point>, ::taihe::error> makePointArray(int32_t n)
{
    taihe::array<Point> arr(n);
    for (int32_t i = 0; i < n; i++) {
        arr[i] = {static_cast<double>(i), static_cast<double>(i * i)};
    }
    return arr;
}

}  // namespace

TH_EXPORT_CPP_API_makeColor(makeColor);
TH_EXPORT_CPP_API_mixColors(mixColors);
TH_EXPORT_CPP_API_makePoint(makePoint);
TH_EXPORT_CPP_API_distance(distance);
TH_EXPORT_CPP_API_makeNamedPoint(makeNamedPoint);
TH_EXPORT_CPP_API_describePoint(describePoint);
TH_EXPORT_CPP_API_makeSegment(makeSegment);
TH_EXPORT_CPP_API_segmentLength(segmentLength);
TH_EXPORT_CPP_API_makePointArray(makePointArray);
// NOLINTEND
