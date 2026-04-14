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
#include "bigint.impl.hpp"
#include "bigint.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

// All Taihe big integers are represented as 2's complement big integers,
// which means the sign bit is the most significant bit of the last byte.
// The sign bit is 1 if the number is negative, and 0 if the number is
// non-negative.
// Here are some utility functions to convert between 2's complement big
// integers and their sign and absolute value representations.

// Get most significant or sign bit from an integral type.
template<typename T, std::enable_if_t<std::is_integral_v<T>, int> = 0>
bool get_msb(T dig)
{
    return dig >> (sizeof(T) * 8 - 1) != 0;
}

// Get sign from a 2's complement big integer represented as an array.
//
// For example:
//   get_sign([0x7f]) => false        (+127)
//   get_sign([0x80]) => true         (-128)
//   get_sign([0x80, 0x00]) => false  (+128)
//   get_sign([0x00, 0xff]) => true   (-256)
//   get_sign([0x00]) => false        (   0)
template<typename T, std::enable_if_t<std::is_integral_v<T>, int> = 0>
bool get_sign(taihe::array_view<T> num)
{
    return get_msb(num[num.size() - 1]);
}

// Get sign and absolute value (without additional sign bit) from a 2's
// complement big integer represented as an array.
//
// For example:
//   get_sign_and_abs([0x7f]) => {false, [0x7f]}             (+127)
//   get_sign_and_abs([0x80]) => {true, [0x80]}              (-128)
//   get_sign_and_abs([0x80, 0x00]) => {false, [0x80]}       (+128)
//   get_sign_and_abs([0x00, 0xff]) => {true, [0x00, 0x01]}  (-256)
//   get_sign_and_abs([0x00]) => {false, []}                 (   0)
template<typename T, std::enable_if_t<std::is_integral_v<T>, int> = 0>
std::pair<bool, taihe::array<T>> get_sign_and_abs(taihe::array_view<T> num)
{
    T *buf = reinterpret_cast<T *>(malloc(num.size() * sizeof(T)));
    bool sign = get_msb(num[num.size() - 1]);
    if (sign) {
        bool carry = true;
        for (std::size_t i = 0; i < num.size(); i++) {
            buf[i] = ~num[i] + carry;
            carry = carry && (buf[i] == 0);
        }
    } else {
        for (std::size_t i = 0; i < num.size(); i++) {
            buf[i] = num[i];
        }
    }
    std::size_t size = num.size();
    while (size > 0 && buf[size - 1] == 0) {
        size--;
    }
    return {sign, taihe::array<T>(buf, size)};
}

// Create a 2's complement big integer represented as an array from its sign and
// absolute value.
//
// For example:
//   get_num(false, [0x7f]) => [0x7f, 0x00]       (+127)
//   get_num(true, [0x80]) => [0x80, 0x00]        (-128)
//   get_num(false, [0x80]) => [0x80, 0x00]       (+128)
//   get_num(true, [0x00, 0x01]) => [0x00, 0xff]  (-256)
//   get_num(false, []) => [0x00]                 (   0)
template<typename T, std::enable_if_t<std::is_integral_v<T>, int> = 0>
taihe::array<T> build_num(bool sign, taihe::array_view<T> abs)
{
    T *buf = reinterpret_cast<T *>(malloc((abs.size() + 1) * sizeof(T)));
    if (sign) {
        bool carry = true;
        for (std::size_t i = 0; i < abs.size(); i++) {
            buf[i] = ~abs[i] + carry;
            carry = carry && (buf[i] == 0);
        }
        buf[abs.size()] = carry - 1;
    } else {
        for (std::size_t i = 0; i < abs.size(); i++) {
            buf[i] = abs[i];
        }
        buf[abs.size()] = 0;
    }
    std::size_t size = abs.size() + 1;
    while (size >= 2 && ((buf[size - 1] == 0 && get_msb(buf[size - 2]) == 0) ||
                         (buf[size - 1] == -1 && get_msb(buf[size - 2]) == 1))) {
        size--;
    }
    return taihe::array<T>(buf, size);
}

namespace {
::taihe::expected<taihe::array<uint8_t>, ::taihe::error> processBigInt(taihe::array_view<uint8_t> a)
{
    // Convert a 2's complement big integer to its sign and absolute value.
    auto [sign, abs] = get_sign_and_abs(a);
    // Invert the sign and return the new 2's complement big integer.
    return build_num(!sign, abs);
}
}  // namespace

TH_EXPORT_CPP_API_processBigInt(processBigInt);
// NOLINTEND
