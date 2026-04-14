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
#include "arraybuffer.impl.hpp"

#include <cstdint>
#include <cstring>
#include <numeric>
#include <vector>
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {
uint8_t SumArrayU8(array_view<uint8_t> nums)
{
    return std::accumulate(nums.begin(), nums.end(), 0);
}

::taihe::expected<::taihe::array<uint8_t>, ::taihe::error> GetArrayBuffer(uint8_t nums)
{
    ::taihe::array<uint8_t> result = ::taihe::array<uint8_t>::make(nums);
    std::fill(result.begin(), result.end(), nums);
    return result;
}

::taihe::expected<::taihe::array<uint8_t>, ::taihe::error> DoubleArrayBuffer(array_view<uint8_t> nums)
{
    ::taihe::array<uint8_t> result = ::taihe::array<uint8_t>::make(nums.size());
    constexpr int32_t const mulTwo = 2;
    for (int i = 0; i < nums.size(); i++) {
        result[i] = nums[i] * mulTwo;
    }
    return result;
}

int8_t SumArrayI8(array_view<int8_t> nums)
{
    return std::accumulate(nums.begin(), nums.end(), 0);
}

::taihe::expected<::taihe::array<int8_t>, ::taihe::error> GetArrayI8(int8_t nums)
{
    ::taihe::array<int8_t> result = ::taihe::array<int8_t>::make(nums);
    std::fill(result.begin(), result.end(), nums);
    return result;
}

::taihe::expected<::taihe::array<int8_t>, ::taihe::error> DoubleI8(array_view<int8_t> nums)
{
    ::taihe::array<int8_t> result = ::taihe::array<int8_t>::make(nums.size());
    constexpr int32_t const mulTwo = 2;
    for (int i = 0; i < nums.size(); i++) {
        result[i] = nums[i] * mulTwo;
    }
    return result;
}

::taihe::expected<int16_t, ::taihe::error> SumArrayI16(array_view<int16_t> nums)
{
    return std::accumulate(nums.begin(), nums.end(), 0);
}

::taihe::expected<::taihe::array<int16_t>, ::taihe::error> GetArrayI16(int16_t nums)
{
    ::taihe::array<int16_t> result = ::taihe::array<int16_t>::make(nums);
    std::fill(result.begin(), result.end(), nums);
    return result;
}

::taihe::expected<::taihe::array<int16_t>, ::taihe::error> DoubleI16(array_view<int16_t> nums)
{
    ::taihe::array<int16_t> result = ::taihe::array<int16_t>::make(nums.size());
    constexpr int32_t const mulTwo = 2;
    for (int i = 0; i < nums.size(); i++) {
        result[i] = nums[i] * mulTwo;
    }
    return result;
}

::taihe::expected<int32_t, ::taihe::error> SumArrayI32(array_view<int32_t> nums)
{
    return std::accumulate(nums.begin(), nums.end(), 0);
}

::taihe::expected<::taihe::array<int32_t>, ::taihe::error> GetArrayI32(int32_t nums)
{
    ::taihe::array<int32_t> result = ::taihe::array<int32_t>::make(nums);
    std::fill(result.begin(), result.end(), nums);
    return result;
}

::taihe::expected<::taihe::array<int32_t>, ::taihe::error> DoubleI32(array_view<int32_t> nums)
{
    ::taihe::array<int32_t> result = ::taihe::array<int32_t>::make(nums.size());
    constexpr int32_t const mulTwo = 2;
    for (int i = 0; i < nums.size(); i++) {
        result[i] = nums[i] * mulTwo;
    }
    return result;
}

::taihe::expected<int64_t, ::taihe::error> SumArrayI64(array_view<int64_t> nums)
{
    return std::accumulate(nums.begin(), nums.end(), 0);
}

::taihe::expected<::taihe::array<int64_t>, ::taihe::error> GetArrayI64(int64_t nums)
{
    ::taihe::array<int64_t> result = ::taihe::array<int64_t>::make(nums);
    std::fill(result.begin(), result.end(), nums);
    return result;
}

::taihe::expected<::taihe::array<int64_t>, ::taihe::error> DoubleI64(array_view<int64_t> nums)
{
    ::taihe::array<int64_t> result = ::taihe::array<int64_t>::make(nums.size());
    constexpr int32_t const mulTwo = 2;
    for (int i = 0; i < nums.size(); i++) {
        result[i] = nums[i] * mulTwo;
    }
    return result;
}

::taihe::expected<float, ::taihe::error> SumArrayF32(array_view<float> nums)
{
    return std::accumulate(nums.begin(), nums.end(), 0);
}

::taihe::expected<::taihe::array<float>, ::taihe::error> GetArrayF32(float nums)
{
    ::taihe::array<float> result = ::taihe::array<float>::make(nums);
    std::fill(result.begin(), result.end(), nums);
    return result;
}

::taihe::expected<::taihe::array<float>, ::taihe::error> DoubleF32(array_view<float> nums)
{
    ::taihe::array<float> result = ::taihe::array<float>::make(nums.size());
    constexpr int32_t const mulTwo = 2;
    for (int i = 0; i < nums.size(); i++) {
        result[i] = nums[i] * mulTwo;
    }
    return result;
}

::taihe::expected<double, ::taihe::error> SumArrayF64(array_view<double> nums)
{
    return std::accumulate(nums.begin(), nums.end(), 0);
}

::taihe::expected<::taihe::array<double>, ::taihe::error> GetArrayF64(double nums)
{
    ::taihe::array<double> result = ::taihe::array<double>::make(nums);
    std::fill(result.begin(), result.end(), nums);
    return result;
}

::taihe::expected<::taihe::array<double>, ::taihe::error> DoubleF64(array_view<double> nums)
{
    ::taihe::array<double> result = ::taihe::array<double>::make(nums.size());
    constexpr int32_t const mulTwo = 2;
    for (int i = 0; i < nums.size(); i++) {
        result[i] = nums[i] * mulTwo;
    }
    return result;
}

::taihe::expected<::taihe::array<uint8_t>, ::taihe::error> DoubleBufferToInt8Array(array_view<uint8_t> nums)
{
    if (nums.size() % sizeof(int8_t) != 0) {
        throw std::runtime_error("Invalid buffer size for Int32Array");
    }
    ::taihe::array<uint8_t> result = ::taihe::array<uint8_t>::make(nums.size());
    int8_t *src = reinterpret_cast<int8_t *>(nums.data());
    int8_t *dst = reinterpret_cast<int8_t *>(result.data());
    size_t count = nums.size() / sizeof(int8_t);
    constexpr int32_t const mulTwo = 2;
    for (size_t i = 0; i < count; ++i) {
        dst[i] = src[i] * mulTwo;
    }

    return result;
}

::taihe::expected<::taihe::array<uint8_t>, ::taihe::error> DoubleBufferToInt16Array(array_view<uint8_t> nums)
{
    if (nums.size() % sizeof(int16_t) != 0) {
        throw std::runtime_error("Invalid buffer size for Int32Array");
    }
    ::taihe::array<uint8_t> result = ::taihe::array<uint8_t>::make(nums.size());
    int16_t *src = reinterpret_cast<int16_t *>(nums.data());
    int16_t *dst = reinterpret_cast<int16_t *>(result.data());
    size_t count = nums.size() / sizeof(int16_t);
    constexpr int32_t const mulTwo = 2;
    for (size_t i = 0; i < count; ++i) {
        dst[i] = src[i] * mulTwo;
    }

    return result;
}

::taihe::expected<::taihe::array<uint8_t>, ::taihe::error> DoubleBufferToInt32Array(array_view<uint8_t> nums)
{
    if (nums.size() % sizeof(int32_t) != 0) {
        throw std::runtime_error("Invalid buffer size for Int32Array");
    }
    ::taihe::array<uint8_t> result = ::taihe::array<uint8_t>::make(nums.size());
    int32_t *src = reinterpret_cast<int32_t *>(nums.data());
    int32_t *dst = reinterpret_cast<int32_t *>(result.data());
    size_t count = nums.size() / sizeof(int32_t);
    constexpr int32_t const mulTwo = 2;
    for (size_t i = 0; i < count; ++i) {
        dst[i] = src[i] * mulTwo;
    }

    return result;
}

::taihe::expected<::taihe::array<uint8_t>, ::taihe::error> DoubleBufferToUint16Array(array_view<uint8_t> nums)
{
    if (nums.size() % sizeof(uint16_t) != 0) {
        throw std::runtime_error("Invalid buffer size for Int32Array");
    }
    ::taihe::array<uint8_t> result = ::taihe::array<uint8_t>::make(nums.size());
    uint16_t *src = reinterpret_cast<uint16_t *>(nums.data());
    uint16_t *dst = reinterpret_cast<uint16_t *>(result.data());
    size_t count = nums.size() / sizeof(uint16_t);
    constexpr int32_t const mulTwo = 2;
    for (size_t i = 0; i < count; ++i) {
        dst[i] = src[i] * mulTwo;
    }

    return result;
}

::taihe::expected<::taihe::array<uint8_t>, ::taihe::error> DoubleBufferToUint32Array(array_view<uint8_t> nums)
{
    if (nums.size() % sizeof(uint32_t) != 0) {
        throw std::runtime_error("Invalid buffer size for Int32Array");
    }
    ::taihe::array<uint8_t> result = ::taihe::array<uint8_t>::make(nums.size());
    uint32_t *src = reinterpret_cast<uint32_t *>(nums.data());
    uint32_t *dst = reinterpret_cast<uint32_t *>(result.data());
    size_t count = nums.size() / sizeof(uint32_t);
    constexpr int32_t const mulTwo = 2;
    for (size_t i = 0; i < count; ++i) {
        dst[i] = src[i] * mulTwo;
    }

    return result;
}
}  // namespace

// because these macros are auto-generate, lint will cause false positive.
TH_EXPORT_CPP_API_SumArrayU8(SumArrayU8);
TH_EXPORT_CPP_API_GetArrayBuffer(GetArrayBuffer);
TH_EXPORT_CPP_API_DoubleArrayBuffer(DoubleArrayBuffer);
TH_EXPORT_CPP_API_SumArrayI8(SumArrayI8);
TH_EXPORT_CPP_API_GetArrayI8(GetArrayI8);
TH_EXPORT_CPP_API_DoubleI8(DoubleI8);
TH_EXPORT_CPP_API_SumArrayI16(SumArrayI16);
TH_EXPORT_CPP_API_GetArrayI16(GetArrayI16);
TH_EXPORT_CPP_API_DoubleI16(DoubleI16);
TH_EXPORT_CPP_API_SumArrayI32(SumArrayI32);
TH_EXPORT_CPP_API_GetArrayI32(GetArrayI32);
TH_EXPORT_CPP_API_DoubleI32(DoubleI32);
TH_EXPORT_CPP_API_SumArrayI64(SumArrayI64);
TH_EXPORT_CPP_API_GetArrayI64(GetArrayI64);
TH_EXPORT_CPP_API_DoubleI64(DoubleI64);
TH_EXPORT_CPP_API_SumArrayF32(SumArrayF32);
TH_EXPORT_CPP_API_GetArrayF32(GetArrayF32);
TH_EXPORT_CPP_API_DoubleF32(DoubleF32);
TH_EXPORT_CPP_API_SumArrayF64(SumArrayF64);
TH_EXPORT_CPP_API_GetArrayF64(GetArrayF64);
TH_EXPORT_CPP_API_DoubleF64(DoubleF64);
TH_EXPORT_CPP_API_DoubleBufferToInt8Array(DoubleBufferToInt8Array);
TH_EXPORT_CPP_API_DoubleBufferToInt16Array(DoubleBufferToInt16Array);
TH_EXPORT_CPP_API_DoubleBufferToInt32Array(DoubleBufferToInt32Array);
TH_EXPORT_CPP_API_DoubleBufferToUint16Array(DoubleBufferToUint16Array);
TH_EXPORT_CPP_API_DoubleBufferToUint32Array(DoubleBufferToUint32Array);
// NOLINTEND