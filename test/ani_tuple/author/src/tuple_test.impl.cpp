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
#include "tuple_test.impl.hpp"
#include "tuple_test.proj.hpp"

#include <sstream>
#include <string>

using namespace taihe;
using namespace tuple_test;

namespace {

// --- IntPair tests ---

IntPair MakeIntPair(int32_t a, int32_t b)
{
    return {a, b};
}

int32_t SumIntPair(IntPair const &p)
{
    return p.first + p.second;
}

IntPair SwapIntPair(IntPair const &p)
{
    return {p.second, p.first};
}

// --- MixedTuple tests ---

MixedTuple ProcessMixed(MixedTuple const &m)
{
    return {
        static_cast<int8_t>(m.a + 1), static_cast<int16_t>(m.b + 2), m.c + 3, m.d + 4, m.e + 5.0f, m.f + 6.0, !m.g,
    };
}

// --- StringPair tests ---

StringPair MakeStringPair(string_view k, string_view v)
{
    return {k, v};
}

string ConcatStringPair(StringPair const &p)
{
    return string(std::string(p.key.data(), p.key.size()) + ":" + std::string(p.value.data(), p.value.size()));
}

// --- MixedRefTuple tests ---

MixedRefTuple MakeMixedRef(string_view name, int32_t age, double score, bool active)
{
    return {name, age, score, active};
}

string DescribeMixedRef(MixedRefTuple const &m)
{
    std::ostringstream oss;
    oss << std::string(m.name.data(), m.name.size()) << "," << m.age << "," << m.score << ","
        << (m.active ? "true" : "false");
    return string(oss.str());
}

// --- Array<IntPair> tests ---

array<IntPair> MakeIntPairArray(int32_t n)
{
    static constexpr int32_t v = 10;
    array<IntPair> arr(n);
    for (int32_t i = 0; i < n; i++) {
        arr[i] = {i, i * v};
    }
    return arr;
}

int32_t SumIntPairArray(array_view<IntPair> pairs)
{
    int32_t total = 0;
    for (size_t i = 0; i < pairs.size(); i++) {
        total += pairs[i].first + pairs[i].second;
    }
    return total;
}

// --- ArrayTuple tests ---

ArrayTuple MakeArrayTuple(string_view label, int32_t n)
{
    static constexpr int32_t v = 10;
    array<int32_t> values(n);
    for (int32_t i = 0; i < n; i++) {
        values[i] = (i + 1) * v;
    }
    return {label, std::move(values)};
}

string SumArrayTuple(ArrayTuple const &t)
{
    int32_t total = 0;
    for (size_t i = 0; i < t.values.size(); i++) {
        total += t.values[i];
    }
    std::ostringstream oss;
    oss << std::string(t.label.data(), t.label.size()) << ":" << total;
    return string(oss.str());
}

MyTuple4x4 TransposeMyTuple4x4(MyTuple4x4 const &t)
{
    return {
        .a =
            {
                .a = t.a.a,
                .b = t.b.a,
                .c = t.c.a,
                .d = t.d.a,
            },
        .b =
            {
                .a = t.a.b,
                .b = t.b.b,
                .c = t.c.b,
                .d = t.d.b,
            },
        .c =
            {
                .a = t.a.c,
                .b = t.b.c,
                .c = t.c.c,
                .d = t.d.c,
            },
        .d =
            {
                .a = t.a.d,
                .b = t.b.d,
                .c = t.c.d,
                .d = t.d.d,
            },
    };
}

array<MyTuple4> TransposeMyTuple4Array(MyTuple4Array const &t)
{
    size_t maxSize = 0;
    if (t.a.size() > maxSize) {
        maxSize = t.a.size();
    }
    if (t.b.size() > maxSize) {
        maxSize = t.b.size();
    }
    if (t.c.size() > maxSize) {
        maxSize = t.c.size();
    }
    if (t.d.size() > maxSize) {
        maxSize = t.d.size();
    }
    array<MyTuple4> result(maxSize);
    for (size_t i = 0; i < maxSize; i++) {
        result[i] = {
            .a = i < t.a.size() ? t.a[i] : 0,
            .b = i < t.b.size() ? t.b[i] : 0,
            .c = i < t.c.size() ? t.c[i] : 0,
            .d = i < t.d.size() ? t.d[i] : 0,
        };
    }
    return result;
}

MyTuple4Array TransposeArrayMyTuple4(array_view<MyTuple4> t)
{
    size_t length = t.size();
    MyTuple4Array result {
        .a = array<int32_t>(length),
        .b = array<int32_t>(length),
        .c = array<int32_t>(length),
        .d = array<int32_t>(length),
    };
    for (size_t i = 0; i < length; i++) {
        result.a[i] = t[i].a;
        result.b[i] = t[i].b;
        result.c[i] = t[i].c;
        result.d[i] = t[i].d;
    }
    return result;
}

MyTuple16 MakeMyTuple16(int32_t p0, int32_t p1, int32_t p2, int32_t p3, int32_t p4, int32_t p5, int32_t p6, int32_t p7,
                        int32_t p8, int32_t p9, int32_t pa, int32_t pb, int32_t pc, int32_t pd, int32_t pe, int32_t pf)
{
    return {
        .f0 = p0,
        .f1 = p1,
        .f2 = p2,
        .f3 = p3,
        .f4 = p4,
        .f5 = p5,
        .f6 = p6,
        .f7 = p7,
        .f8 = p8,
        .f9 = p9,
        .fa = pa,
        .fb = pb,
        .fc = pc,
        .fd = pd,
        .fe = pe,
        .ff = pf,
    };
}

int32_t SumMyTuple16(MyTuple16 const &t)
{
    int32_t result = 0;
    result += t.f0;
    result += t.f1;
    result += t.f2;
    result += t.f3;
    result += t.f4;
    result += t.f5;
    result += t.f6;
    result += t.f7;
    result += t.f8;
    result += t.f9;
    result += t.fa;
    result += t.fb;
    result += t.fc;
    result += t.fd;
    result += t.fe;
    result += t.ff;
    return result;
}

}  // namespace

// Since these macros are auto-generated, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_MakeIntPair(MakeIntPair);
TH_EXPORT_CPP_API_SumIntPair(SumIntPair);
TH_EXPORT_CPP_API_SwapIntPair(SwapIntPair);
TH_EXPORT_CPP_API_ProcessMixed(ProcessMixed);
TH_EXPORT_CPP_API_MakeStringPair(MakeStringPair);
TH_EXPORT_CPP_API_ConcatStringPair(ConcatStringPair);
TH_EXPORT_CPP_API_MakeMixedRef(MakeMixedRef);
TH_EXPORT_CPP_API_DescribeMixedRef(DescribeMixedRef);
TH_EXPORT_CPP_API_MakeIntPairArray(MakeIntPairArray);
TH_EXPORT_CPP_API_SumIntPairArray(SumIntPairArray);
TH_EXPORT_CPP_API_MakeArrayTuple(MakeArrayTuple);
TH_EXPORT_CPP_API_SumArrayTuple(SumArrayTuple);
TH_EXPORT_CPP_API_TransposeMyTuple4x4(TransposeMyTuple4x4);
TH_EXPORT_CPP_API_TransposeMyTuple4Array(TransposeMyTuple4Array);
TH_EXPORT_CPP_API_TransposeArrayMyTuple4(TransposeArrayMyTuple4);
TH_EXPORT_CPP_API_MakeMyTuple16(MakeMyTuple16);
TH_EXPORT_CPP_API_SumMyTuple16(SumMyTuple16);
// NOLINTEND
