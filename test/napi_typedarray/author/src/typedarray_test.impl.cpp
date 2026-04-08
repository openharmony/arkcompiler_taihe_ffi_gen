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

#include "typedarray_test.impl.hpp"
#include <complex.h>
#include <iostream>
#include <numeric>
#include "typedarray_test.proj.hpp"

#include <cmath>
#include <iomanip>
#include <limits>

namespace {
class TypedArrInfoImpl {
public:
    ::taihe::array<uint8_t> uint8Arr = {1, 2, 3, 4, 5};
    ::taihe::array<int8_t> int8Arr = {1, -2, 3, -4, 5};
    ::taihe::array<uint16_t> uint16Arr = {10, 20, 30, 40, 50};
    ::taihe::array<int16_t> int16Arr = {10, -20, 30, -40, 50};
    ::taihe::array<uint32_t> uint32Arr = {100, 200, 300, 400, 500};
    ::taihe::array<int32_t> int32Arr = {100, -200, 300, -400, 500};
    ::taihe::array<uint64_t> uint64Arr = {1000, 2000, 3000, 4000, 5000};
    ::taihe::array<int64_t> int64Arr = {1000, -2000, 3000, -4000, 5000};
    ::taihe::array<float> float32Arr = {1.0f, 2.0f, 3.0f, 4.0f, 5.0f};
    ::taihe::array<double> float64Arr = {1.0, 2.0, 3.0, 4.0, 5.0};

    ::taihe::expected<void, ::taihe::error> CreateUint8Array(::taihe::array_view<uint8_t> a)
    {
        this->uint8Arr = a;
        std::cout << "createUint8Array uint8Arr length: " << this->uint8Arr.size() << std::endl;
        std::cout << "createUint8Array uint8Arr value: ";
        for (auto val : this->uint8Arr) {
            std::cout << static_cast<int>(val) << " ";
        }
        std::cout << std::endl;
        return {};
    }

    ::taihe::expected<::taihe::array<uint8_t>, ::taihe::error> PrintUint8Array(::taihe::array_view<uint8_t> a)
    {
        this->uint8Arr = a;
        return this->uint8Arr;
    }

    ::taihe::expected<void, ::taihe::error> SetUint8Array(::taihe::array_view<uint8_t> a)
    {
        this->uint8Arr = a;
        std::cout << "setUint8Array uint8Arr length: " << this->uint8Arr.size() << std::endl;
        std::cout << "setUint8Array uint8Arr value: ";
        for (auto val : this->uint8Arr) {
            std::cout << static_cast<int>(val) << " ";
        }
        std::cout << std::endl;
        return {};
    }

    ::taihe::expected<::taihe::array<uint8_t>, ::taihe::error> GetUint8Array()
    {
        return this->uint8Arr;
    }

    ::taihe::expected<void, ::taihe::error> CreateInt8Array(::taihe::array_view<int8_t> a)
    {
        this->int8Arr = a;
        std::cout << "createInt8Array int8Arr length: " << this->int8Arr.size() << std::endl;
        std::cout << "createInt8Array int8Arr value: ";
        for (auto val : this->int8Arr) {
            std::cout << static_cast<int>(val) << " ";
        }
        std::cout << std::endl;
        return {};
    }

    ::taihe::expected<::taihe::array<int8_t>, ::taihe::error> PrintInt8Array(::taihe::array_view<int8_t> a)
    {
        this->int8Arr = a;
        return this->int8Arr;
    }

    void SetInt8Array(::taihe::array_view<int8_t> a)
    {
        this->int8Arr = a;
        std::cout << "setInt8Array int8Arr length: " << this->int8Arr.size() << std::endl;
        std::cout << "setInt8Array int8Arr value: ";
        for (auto val : this->int8Arr) {
            std::cout << static_cast<int>(val) << " ";
        }
        std::cout << std::endl;
    }

    ::taihe::expected<::taihe::array<int8_t>, ::taihe::error> GetInt8Array()
    {
        return this->int8Arr;
    }

    void CreateUint16Array(::taihe::array_view<uint16_t> a)
    {
        this->uint16Arr = a;
        std::cout << "createUint16Array uint16Arr length: " << this->uint16Arr.size() << std::endl;
        std::cout << "createUint16Array uint16Arr value: ";
        for (auto val : this->uint16Arr) {
            std::cout << val << " ";
        }
        std::cout << std::endl;
    }

    ::taihe::expected<::taihe::array<uint16_t>, ::taihe::error> PrintUint16Array(::taihe::array_view<uint16_t> a)
    {
        this->uint16Arr = a;
        return this->uint16Arr;
    }

    void SetUint16Array(::taihe::array_view<uint16_t> a)
    {
        this->uint16Arr = a;
        std::cout << "setUint16Array uint16Arr length: " << this->uint16Arr.size() << std::endl;
        std::cout << "setUint16Array uint16Arr value: ";
        for (auto val : this->uint16Arr) {
            std::cout << val << " ";
        }
        std::cout << std::endl;
    }

    ::taihe::expected<::taihe::array<uint16_t>, ::taihe::error> GetUint16Array()
    {
        return this->uint16Arr;
    }

    void CreateInt16Array(::taihe::array_view<int16_t> a)
    {
        this->int16Arr = a;
        std::cout << "createInt16Array int16Arr length: " << this->int16Arr.size() << std::endl;
        std::cout << "createInt16Array int16Arr value: ";
        for (auto val : this->int16Arr) {
            std::cout << val << " ";
        }
        std::cout << std::endl;
    }

    ::taihe::expected<::taihe::array<int16_t>, ::taihe::error> PrintInt16Array(::taihe::array_view<int16_t> a)
    {
        this->int16Arr = a;
        return this->int16Arr;
    }

    void SetInt16Array(::taihe::array_view<int16_t> a)
    {
        this->int16Arr = a;
        std::cout << "setInt16Array int16Arr length: " << this->int16Arr.size() << std::endl;
        std::cout << "setInt16Array int16Arr value: ";
        for (auto val : this->int16Arr) {
            std::cout << val << " ";
        }
        std::cout << std::endl;
    }

    ::taihe::expected<::taihe::array<int16_t>, ::taihe::error> GetInt16Array()
    {
        return this->int16Arr;
    }

    void CreateUint32Array(::taihe::array_view<uint32_t> a)
    {
        this->uint32Arr = a;
        std::cout << "createUint32Array uint32Arr length: " << this->uint32Arr.size() << std::endl;
        std::cout << "createUint32Array uint32Arr value: ";
        for (auto val : this->uint32Arr) {
            std::cout << val << " ";
        }
        std::cout << std::endl;
    }

    ::taihe::expected<::taihe::array<uint32_t>, ::taihe::error> PrintUint32Array(::taihe::array_view<uint32_t> a)
    {
        this->uint32Arr = a;
        return this->uint32Arr;
    }

    void SetUint32Array(::taihe::array_view<uint32_t> a)
    {
        this->uint32Arr = a;
        std::cout << "setUint32Array uint32Arr length: " << this->uint32Arr.size() << std::endl;
        std::cout << "setUint32Array uint32Arr value: ";
        for (auto val : this->uint32Arr) {
            std::cout << val << " ";
        }
        std::cout << std::endl;
    }

    ::taihe::expected<::taihe::array<uint32_t>, ::taihe::error> GetUint32Array()
    {
        return this->uint32Arr;
    }

    void CreateInt32Array(::taihe::array_view<int32_t> a)
    {
        this->int32Arr = a;
        std::cout << "createInt32Array int32Arr length: " << this->int32Arr.size() << std::endl;
        std::cout << "createInt32Array int32Arr value: ";
        for (auto val : this->int32Arr) {
            std::cout << val << " ";
        }
        std::cout << std::endl;
    }

    ::taihe::expected<::taihe::array<int32_t>, ::taihe::error> PrintInt32Array(::taihe::array_view<int32_t> a)
    {
        this->int32Arr = a;
        return this->int32Arr;
    }

    void SetInt32Array(::taihe::array_view<int32_t> a)
    {
        this->int32Arr = a;
        std::cout << "setInt32Array int32Arr length: " << this->int32Arr.size() << std::endl;
        std::cout << "setInt32Array int32Arr value: ";
        for (auto val : this->int32Arr) {
            std::cout << val << " ";
        }
        std::cout << std::endl;
    }

    ::taihe::expected<::taihe::array<int32_t>, ::taihe::error> GetInt32Array()
    {
        return this->int32Arr;
    }

    void CreateUint64Array(::taihe::array_view<uint64_t> a)
    {
        this->uint64Arr = a;
        std::cout << "createUint64Array uint64Arr length: " << this->uint64Arr.size() << std::endl;
        std::cout << "createUint64Array uint64Arr value: ";
        for (auto val : this->uint64Arr) {
            std::cout << val << " ";
        }
        std::cout << std::endl;
    }

    ::taihe::expected<::taihe::array<uint64_t>, ::taihe::error> PrintUint64Array(::taihe::array_view<uint64_t> a)
    {
        this->uint64Arr = a;
        return this->uint64Arr;
    }

    void SetUint64Array(::taihe::array_view<uint64_t> a)
    {
        this->uint64Arr = a;
        std::cout << "setUint64Array uint64Arr length: " << this->uint64Arr.size() << std::endl;
        std::cout << "setUint64Array uint64Arr value: ";
        for (auto val : this->uint64Arr) {
            std::cout << val << " ";
        }
        std::cout << std::endl;
    }

    ::taihe::expected<::taihe::array<uint64_t>, ::taihe::error> GetUint64Array()
    {
        return this->uint64Arr;
    }

    void CreateInt64Array(::taihe::array_view<int64_t> a)
    {
        this->int64Arr = a;
        std::cout << "createInt64Array int64Arr length: " << this->int64Arr.size() << std::endl;
        std::cout << "createInt64Array int64Arr value: ";
        for (auto val : this->int64Arr) {
            std::cout << static_cast<long long>(val) << " ";
        }
        std::cout << std::endl;
    }

    ::taihe::expected<::taihe::array<int64_t>, ::taihe::error> PrintInt64Array(::taihe::array_view<int64_t> a)
    {
        this->int64Arr = a;
        return this->int64Arr;
    }

    void SetInt64Array(::taihe::array_view<int64_t> a)
    {
        this->int64Arr = a;
        std::cout << "setInt64Array int64Arr length: " << this->int64Arr.size() << std::endl;
        std::cout << "setInt64Array int64Arr value: ";
        for (auto val : this->int64Arr) {
            std::cout << static_cast<long long>(val) << " ";
        }
        std::cout << std::endl;
    }

    ::taihe::expected<::taihe::array<int64_t>, ::taihe::error> GetInt64Array()
    {
        return this->int64Arr;
    }

    void CreateFloat32Array(::taihe::array_view<float> a)
    {
        this->float32Arr = a;
        std::cout << "createFloat32Array float32Arr length: " << this->float32Arr.size() << std::endl;
        std::cout << "createFloat32Array float32Arr value: ";
        for (auto val : this->float32Arr) {
            std::cout << val << " ";
        }
        std::cout << std::endl;
    }

    ::taihe::expected<::taihe::array<float>, ::taihe::error> PrintFloat32Array(::taihe::array_view<float> a)
    {
        this->float32Arr = a;
        return this->float32Arr;
    }

    void SetFloat32Array(::taihe::array_view<float> a)
    {
        this->float32Arr = a;
        std::cout << "setFloat32Array float32Arr length: " << this->float32Arr.size() << std::endl;
        std::cout << "setFloat32Array float32Arr value: ";
        for (auto val : this->float32Arr) {
            std::cout << val << " ";
        }
        std::cout << std::endl;
    }

    ::taihe::expected<::taihe::array<float>, ::taihe::error> GetFloat32Array()
    {
        return this->float32Arr;
    }

    void CreateFloat64Array(::taihe::array_view<double> a)
    {
        this->float64Arr = a;
        std::cout << "createFloat64Array float64Arr length: " << this->float64Arr.size() << std::endl;
        std::cout << "createFloat64Array float64Arr value: ";
        for (auto val : this->float64Arr) {
            std::cout << val << " ";
        }
        std::cout << std::endl;
    }

    ::taihe::expected<::taihe::array<double>, ::taihe::error> PrintFloat64Array(::taihe::array_view<double> a)
    {
        this->float64Arr = a;
        return this->float64Arr;
    }

    void SetFloat64Array(::taihe::array_view<double> a)
    {
        this->float64Arr = a;
        std::cout << "setFloat64Array float64Arr length: " << this->float64Arr.size() << std::endl;
        std::cout << "setFloat64Array float64Arr value: ";
        for (auto val : this->float64Arr) {
            std::cout << val << " ";
        }
        std::cout << std::endl;
    }

    ::taihe::expected<::taihe::array<double>, ::taihe::error> GetFloat64Array()
    {
        return this->float64Arr;
    }

    ::taihe::expected<::taihe::array<int32_t>, ::taihe::error> GetUint8ArrayOptional(
        ::taihe::optional_view<::taihe::array<uint8_t>> a)
    {
        if (!a.has_value()) {
            return ::taihe::array<int32_t>(0);
        }
        auto const &src = a.value();
        ::taihe::array<int32_t> result(src.size());
        for (size_t i = 0; i < src.size(); ++i) {
            result[i] = static_cast<int32_t>(src[i]);
        }
        return result;
    }

    ::taihe::expected<::taihe::array<int32_t>, ::taihe::error> GetInt8ArrayOptional(
        ::taihe::optional_view<::taihe::array<int8_t>> a)
    {
        if (!a.has_value()) {
            return ::taihe::array<int32_t>(0);
        }
        auto const &src = a.value();
        ::taihe::array<int32_t> result(src.size());
        for (size_t i = 0; i < src.size(); ++i) {
            result[i] = static_cast<int32_t>(src[i]);
        }
        return result;
    }

    ::taihe::expected<::taihe::array<int32_t>, ::taihe::error> GetUint16ArrayOptional(
        ::taihe::optional_view<::taihe::array<uint16_t>> a)
    {
        if (!a.has_value()) {
            return ::taihe::array<int32_t>(0);
        }
        auto const &src = a.value();
        ::taihe::array<int32_t> result(src.size());
        for (size_t i = 0; i < src.size(); ++i) {
            result[i] = static_cast<int32_t>(src[i]);
        }
        return result;
    }

    ::taihe::expected<::taihe::array<int32_t>, ::taihe::error> GetInt16ArrayOptional(
        ::taihe::optional_view<::taihe::array<int16_t>> a)
    {
        if (!a.has_value()) {
            return ::taihe::array<int32_t>(0);
        }
        auto const &src = a.value();
        ::taihe::array<int32_t> result(src.size());
        for (size_t i = 0; i < src.size(); ++i) {
            result[i] = static_cast<int32_t>(src[i]);
        }
        return result;
    }

    ::taihe::expected<::taihe::array<int32_t>, ::taihe::error> GetUint32ArrayOptional(
        ::taihe::optional_view<::taihe::array<uint32_t>> a)
    {
        if (!a.has_value()) {
            return ::taihe::array<int32_t>(0);
        }
        auto const &src = a.value();
        ::taihe::array<int32_t> result(src.size());
        for (size_t i = 0; i < src.size(); ++i) {
            if (src[i] > static_cast<uint32_t>(std::numeric_limits<int32_t>::max())) {
                result[i] = std::numeric_limits<int32_t>::max();
            } else {
                result[i] = static_cast<int32_t>(src[i]);
            }
        }
        return result;
    }

    ::taihe::expected<::taihe::array<int32_t>, ::taihe::error> GetInt32ArrayOptional(
        ::taihe::optional_view<::taihe::array<int32_t>> a)
    {
        if (!a.has_value()) {
            return ::taihe::array<int32_t>(0);
        }
        return a.value();
    }

    ::taihe::expected<::taihe::array<int32_t>, ::taihe::error> GetUint64ArrayOptional(
        ::taihe::optional_view<::taihe::array<uint64_t>> a)
    {
        if (!a.has_value()) {
            return ::taihe::array<int32_t>(0);
        }
        auto const &src = a.value();
        ::taihe::array<int32_t> result(src.size());
        for (size_t i = 0; i < src.size(); ++i) {
            uint64_t const val = src[i];
            if (val > static_cast<uint64_t>(std::numeric_limits<int32_t>::max())) {
                result[i] = std::numeric_limits<int32_t>::max();
            } else {
                result[i] = static_cast<int32_t>(val);
            }
        }
        return result;
    }

    ::taihe::expected<::taihe::array<int32_t>, ::taihe::error> GetInt64ArrayOptional(
        ::taihe::optional_view<::taihe::array<int64_t>> a)
    {
        if (!a.has_value()) {
            return ::taihe::array<int32_t>(0);
        }
        auto const &src = a.value();
        ::taihe::array<int32_t> result(src.size());
        for (size_t i = 0; i < src.size(); ++i) {
            int64_t const val = src[i];
            if (val < std::numeric_limits<int32_t>::min()) {
                result[i] = std::numeric_limits<int32_t>::min();
            } else if (val > std::numeric_limits<int32_t>::max()) {
                result[i] = std::numeric_limits<int32_t>::max();
            } else {
                result[i] = static_cast<int32_t>(val);
            }
        }
        return result;
    }

    ::taihe::expected<::taihe::array<int32_t>, ::taihe::error> GetFloat32ArrayOptional(
        ::taihe::optional_view<::taihe::array<float>> a)
    {
        if (!a.has_value()) {
            return ::taihe::array<int32_t>(0);
        }
        auto const &src = a.value();
        ::taihe::array<int32_t> result(src.size());
        for (size_t i = 0; i < src.size(); ++i) {
            float const val = src[i];
            if (std::isnan(val)) {
                // 处理非数字
                std::cout << "NaN" << std::endl;
                // taihe::set_error("NaN value is not allowed!");
            }
            // 处理数据溢出
            if (val < static_cast<float>(std::numeric_limits<int32_t>::min())) {
                result[i] = std::numeric_limits<int32_t>::min();
            } else if (val > static_cast<float>(std::numeric_limits<int32_t>::max())) {
                result[i] = std::numeric_limits<int32_t>::max();
            } else {
                result[i] = static_cast<int32_t>(val);
            }
        }
        return result;
    }

    ::taihe::expected<::taihe::array<int32_t>, ::taihe::error> GetFloat64ArrayOptional(
        ::taihe::optional_view<::taihe::array<double>> a)
    {
        if (!a.has_value()) {
            return ::taihe::array<int32_t>(0);
        }
        auto const &src = a.value();
        ::taihe::array<int32_t> result(src.size());
        for (size_t i = 0; i < src.size(); ++i) {
            double const val = src[i];
            if (std::isnan(val)) {
                std::cout << "NaN" << std::endl;
                // taihe::set_error("NaN value is not allowed!");
            }
            if (val < static_cast<double>(std::numeric_limits<int32_t>::min())) {
                result[i] = std::numeric_limits<int32_t>::min();
            } else if (val > static_cast<double>(std::numeric_limits<int32_t>::max())) {
                result[i] = std::numeric_limits<int32_t>::max();
            } else {
                result[i] = static_cast<int32_t>(val);
            }
        }
        return result;
    }

    ::taihe::expected<::taihe::map<::taihe::string, ::taihe::array<uint8_t>>, ::taihe::error> MapUint8Arrays(
        ::taihe::map_view<::taihe::string, ::taihe::array<uint8_t>> m)
    {
        ::taihe::map<::taihe::string, ::taihe::array<uint8_t>> result;
        for (auto const &val : m) {
            result.emplace(val.first, val.second);
        }
        return result;
    }

    ::taihe::expected<::taihe::map<::taihe::string, ::taihe::array<int8_t>>, ::taihe::error> MapInt8Arrays(
        ::taihe::map_view<::taihe::string, ::taihe::array<int8_t>> m)
    {
        ::taihe::map<::taihe::string, ::taihe::array<int8_t>> result;
        for (auto const &val : m) {
            result.emplace(val.first, val.second);
        }
        return result;
    }

    ::taihe::expected<::taihe::map<::taihe::string, ::taihe::array<uint16_t>>, ::taihe::error> MapUint16Arrays(
        ::taihe::map_view<::taihe::string, ::taihe::array<uint16_t>> m)
    {
        ::taihe::map<::taihe::string, ::taihe::array<uint16_t>> result;
        for (auto const &val : m) {
            result.emplace(val.first, val.second);
        }
        return result;
    }

    ::taihe::expected<::taihe::map<::taihe::string, ::taihe::array<int16_t>>, ::taihe::error> MapInt16Arrays(
        ::taihe::map_view<::taihe::string, ::taihe::array<int16_t>> m)
    {
        ::taihe::map<::taihe::string, ::taihe::array<int16_t>> result;
        for (auto const &val : m) {
            result.emplace(val.first, val.second);
        }
        return result;
    }

    ::taihe::expected<::taihe::map<::taihe::string, ::taihe::array<uint32_t>>, ::taihe::error> MapUint32Arrays(
        ::taihe::map_view<::taihe::string, ::taihe::array<uint32_t>> m)
    {
        ::taihe::map<::taihe::string, ::taihe::array<uint32_t>> result;
        for (auto const &val : m) {
            result.emplace(val.first, val.second);
        }
        return result;
    }

    ::taihe::expected<::taihe::map<::taihe::string, ::taihe::array<int32_t>>, ::taihe::error> MapInt32Arrays(
        ::taihe::map_view<::taihe::string, ::taihe::array<int32_t>> m)
    {
        ::taihe::map<::taihe::string, ::taihe::array<int32_t>> result;
        for (auto const &val : m) {
            result.emplace(val.first, val.second);
        }
        return result;
    }

    ::taihe::expected<::taihe::map<::taihe::string, ::taihe::array<uint64_t>>, ::taihe::error> MapUint64Arrays(
        ::taihe::map_view<::taihe::string, ::taihe::array<uint64_t>> m)
    {
        ::taihe::map<::taihe::string, ::taihe::array<uint64_t>> result;
        for (auto const &val : m) {
            result.emplace(val.first, val.second);
        }
        return result;
    }

    ::taihe::expected<::taihe::map<::taihe::string, ::taihe::array<int64_t>>, ::taihe::error> MapInt64Arrays(
        ::taihe::map_view<::taihe::string, ::taihe::array<int64_t>> m)
    {
        ::taihe::map<::taihe::string, ::taihe::array<int64_t>> result;
        for (auto const &val : m) {
            result.emplace(val.first, val.second);
        }
        return result;
    }

    ::taihe::expected<::taihe::map<::taihe::string, ::taihe::array<float>>, ::taihe::error> MapFloat32Arrays(
        ::taihe::map_view<::taihe::string, ::taihe::array<float>> m)
    {
        ::taihe::map<::taihe::string, ::taihe::array<float>> result;
        for (auto const &val : m) {
            result.emplace(val.first, val.second);
        }
        return result;
    }

    ::taihe::expected<::taihe::map<::taihe::string, ::taihe::array<double>>, ::taihe::error> MapFloat64Arrays(
        ::taihe::map_view<::taihe::string, ::taihe::array<double>> m)
    {
        ::taihe::map<::taihe::string, ::taihe::array<double>> result;
        for (auto const &val : m) {
            result.emplace(val.first, val.second);
        }
        return result;
    }
};

::taihe::expected<int32_t, ::taihe::error> SumUint8Array(::taihe::array_view<uint8_t> v)
{
    return std::accumulate(v.begin(), v.end(), 0);
}

::taihe::expected<::taihe::array<uint8_t>, ::taihe::error> NewUint8Array(int64_t n, int32_t v)
{
    ::taihe::array<uint8_t> result(n);
    std::fill(result.begin(), result.end(), v);
    return result;
}

::taihe::expected<int32_t, ::taihe::error> SumUint16Array(::taihe::array_view<uint16_t> v)
{
    return std::accumulate(v.begin(), v.end(), 0);
}

::taihe::expected<::taihe::array<uint16_t>, ::taihe::error> NewUint16Array(int64_t n, int32_t v)
{
    ::taihe::array<uint16_t> result(n);
    std::fill(result.begin(), result.end(), v);
    return result;
}

::taihe::expected<int32_t, ::taihe::error> SumUint32Array(::taihe::array_view<uint32_t> v)
{
    return std::accumulate(v.begin(), v.end(), 0);
}

::taihe::expected<::taihe::array<uint32_t>, ::taihe::error> NewUint32Array(int64_t n, int32_t v)
{
    ::taihe::array<uint32_t> result(n);
    std::fill(result.begin(), result.end(), v);
    return result;
}

::taihe::expected<int64_t, ::taihe::error> SumBigUint64Array(::taihe::array_view<uint64_t> v)
{
    return std::accumulate(v.begin(), v.end(), 0);
}

::taihe::expected<::taihe::array<uint64_t>, ::taihe::error> NewBigUint64Array(int64_t n, int64_t v)
{
    ::taihe::array<uint64_t> result(n);
    std::fill(result.begin(), result.end(), v);
    return result;
}

::taihe::expected<int32_t, ::taihe::error> SumInt8Array(::taihe::array_view<int8_t> v)
{
    return std::accumulate(v.begin(), v.end(), 0);
}

::taihe::expected<::taihe::array<int8_t>, ::taihe::error> NewInt8Array(int64_t n, int32_t v)
{
    ::taihe::array<int8_t> result(n);
    std::fill(result.begin(), result.end(), v);
    return result;
}

::taihe::expected<int32_t, ::taihe::error> SumInt16Array(::taihe::array_view<int16_t> v)
{
    return std::accumulate(v.begin(), v.end(), 0);
}

::taihe::expected<::taihe::array<int16_t>, ::taihe::error> NewInt16Array(int64_t n, int32_t v)
{
    ::taihe::array<int16_t> result(n);
    std::fill(result.begin(), result.end(), v);
    return result;
}

::taihe::expected<int32_t, ::taihe::error> SumInt32Array(::taihe::array_view<int32_t> v)
{
    return std::accumulate(v.begin(), v.end(), 0);
}

::taihe::expected<::taihe::array<int32_t>, ::taihe::error> NewInt32Array(int64_t n, int32_t v)
{
    ::taihe::array<int32_t> result(n);
    std::fill(result.begin(), result.end(), v);
    return result;
}

::taihe::expected<int64_t, ::taihe::error> SumBigInt64Array(::taihe::array_view<int64_t> v)
{
    return std::accumulate(v.begin(), v.end(), 0);
}

::taihe::expected<::taihe::array<int64_t>, ::taihe::error> NewBigInt64Array(int64_t n, int64_t v)
{
    ::taihe::array<int64_t> result(n);
    std::fill(result.begin(), result.end(), v);
    return result;
}

::taihe::expected<double, ::taihe::error> SumFloat32Array(::taihe::array_view<float> v)
{
    return std::accumulate(v.begin(), v.end(), 0.0);
}

::taihe::expected<::taihe::array<float>, ::taihe::error> NewFloat32Array(int64_t n, double v)
{
    ::taihe::array<float> result(n);
    std::fill(result.begin(), result.end(), v);
    return result;
}

::taihe::expected<double, ::taihe::error> SumFloat64Array(::taihe::array_view<double> v)
{
    return std::accumulate(v.begin(), v.end(), 0.0);
}

::taihe::expected<::taihe::array<double>, ::taihe::error> NewFloat64Array(int64_t n, double v)
{
    ::taihe::array<double> result(n);
    std::fill(result.begin(), result.end(), v);
    return result;
}

::taihe::expected<::typedarray_test::TypedArrInfo, ::taihe::error> GetTypedArrInfo()
{
    return ::taihe::make_holder<TypedArrInfoImpl, ::typedarray_test::TypedArrInfo>();
}

template<typename Iterator>
void PrintArray(std::string const &name, Iterator begin, Iterator end)
{
    std::cout << name << ": ";
    for (auto it = begin; it != end; ++it) {
        using ValueType = typename std::iterator_traits<Iterator>::value_type;
        // 处理整数类型（包括 int8_t, uint8_t, int16_t, uint16_t, ...）
        if constexpr (std::is_integral_v<ValueType>) {
            // 特殊处理 uint8_t 和 int8_t（避免被当作字符打印）
            if constexpr (std::is_same_v<ValueType, uint8_t> || std::is_same_v<ValueType, int8_t>) {
                std::cout << static_cast<int>(*it) << " ";
            } else {
                // 其他整型直接打印
                std::cout << *it << " ";
            }
        } else if constexpr (std::is_floating_point_v<ValueType>) {
            // 处理浮点类型（float, double）
            int const precision = 6;
            std::cout << std::fixed << std::setprecision(precision) << *it << " ";
        } else {
            // 其他未知类型（如 bool、char 等）
            std::cout << *it << " ";
        }
    }
    std::cout << std::endl;
}

::taihe::expected<::typedarray_test::TypedArray1, ::taihe::error> SetupStructAndPrint(
    ::typedarray_test::TypedArray1 const &v)
{
    PrintArray("a (Uint8Array)", v.a.begin(), v.a.end());
    PrintArray("b (Int8Array)", v.b.begin(), v.b.end());
    PrintArray("c (Uint16Array)", v.c.begin(), v.c.end());
    PrintArray("d (Int16Array)", v.d.begin(), v.d.end());
    PrintArray("e (Uint32Array)", v.e.begin(), v.e.end());
    PrintArray("f (Int32Array)", v.f.begin(), v.f.end());
    PrintArray("g (Uint64Array)", v.g.begin(), v.g.end());
    PrintArray("h (Int64Array)", v.h.begin(), v.h.end());
    PrintArray("i (Float32Array)", v.i.begin(), v.i.end());
    PrintArray("j (Float64Array)", v.j.begin(), v.j.end());
    return v;
}

}  // namespace

// because these macros are auto-generate, lint will cause false positive.
TH_EXPORT_CPP_API_SumUint8Array(SumUint8Array);
TH_EXPORT_CPP_API_NewUint8Array(NewUint8Array);
TH_EXPORT_CPP_API_SumUint16Array(SumUint16Array);
TH_EXPORT_CPP_API_NewUint16Array(NewUint16Array);
TH_EXPORT_CPP_API_SumUint32Array(SumUint32Array);
TH_EXPORT_CPP_API_NewUint32Array(NewUint32Array);
TH_EXPORT_CPP_API_SumBigUint64Array(SumBigUint64Array);
TH_EXPORT_CPP_API_NewBigUint64Array(NewBigUint64Array);
TH_EXPORT_CPP_API_SumInt8Array(SumInt8Array);
TH_EXPORT_CPP_API_NewInt8Array(NewInt8Array);
TH_EXPORT_CPP_API_SumInt16Array(SumInt16Array);
TH_EXPORT_CPP_API_NewInt16Array(NewInt16Array);
TH_EXPORT_CPP_API_SumInt32Array(SumInt32Array);
TH_EXPORT_CPP_API_NewInt32Array(NewInt32Array);
TH_EXPORT_CPP_API_SumBigInt64Array(SumBigInt64Array);
TH_EXPORT_CPP_API_NewBigInt64Array(NewBigInt64Array);
TH_EXPORT_CPP_API_SumFloat32Array(SumFloat32Array);
TH_EXPORT_CPP_API_NewFloat32Array(NewFloat32Array);
TH_EXPORT_CPP_API_SumFloat64Array(SumFloat64Array);
TH_EXPORT_CPP_API_NewFloat64Array(NewFloat64Array);
TH_EXPORT_CPP_API_GetTypedArrInfo(GetTypedArrInfo);
TH_EXPORT_CPP_API_SetupStructAndPrint(SetupStructAndPrint);
// NOLINTEND