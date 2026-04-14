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
#include "primitives_test.impl.hpp"

#include <iomanip>
#include <iostream>

#include "primitives_test.PrimitivesVoid.proj.2.hpp"
#include "stdexcept"
#include "taihe/optional.hpp"
#include "taihe/runtime.hpp"
#include "taihe/string.hpp"
// Please delete this include when you implement
using namespace taihe;

namespace {
int testInt_add10_ {10};
int testInt_add15_ {15};
int testInt_add32_ {32};
float testFloat_1_ {1.2};
double testDouble_2_ {3.14159};
double testDouble_1_ {3.1};

class PrimitivesVoid {
public:
    ::taihe::expected<void, ::taihe::error> TestBaseFunc1()
    {
        std::cout << "TestBaseFunc1 is true " << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> TestBaseFunc2(int32_t option1, bool option2)
    {
        if (option2) {
            std::cout << "TestBaseFunc2 is option1  " << option1 << std::endl;
            std::cout << "TestBaseFunc2 is option2  " << option2 << std::endl;
        } else {
            std::cout << "TestBaseFunc2 is option1  " << option1 << std::endl;
            std::cout << "TestBaseFunc2 is option2  " << option2 << std::endl;
        }
        return {};
    }

    ::taihe::expected<void, ::taihe::error> TestBaseFunc3(int32_t option1, int64_t option2)
    {
        std::cout << "TestBaseFunc3 is option1  " << option1 << std::endl;
        std::cout << "TestBaseFunc3 is option2  " << option2 << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> TestBaseFunc4(int32_t option1, string_view option2)
    {
        std::cout << "TestBaseFunc4 is option1  " << option1 << std::endl;
        std::cout << "TestBaseFunc4 is option2  " << option2 << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> TestBaseFunc5(int64_t option1, bool option2)
    {
        if (option2) {
            std::cout << "TestBaseFunc5 is option1  " << option1 << std::endl;
            std::cout << "TestBaseFunc5 is option2  " << option2 << std::endl;
        } else {
            std::cout << "TestBaseFunc5 is option1  " << option1 << std::endl;
            std::cout << "TestBaseFunc5 is option2  " << option2 << std::endl;
        }
        return {};
    }

    ::taihe::expected<void, ::taihe::error> TestBaseFunc6(int64_t option1, float option2)
    {
        std::cout << "TestBaseFunc6 is option1  " << option1 << std::endl;
        std::cout << "TestBaseFunc6 is option2  " << option2 << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> TestBaseFunc7(int64_t option1, double option2)
    {
        std::cout << "TestBaseFunc7 is option1  " << option1 << std::endl;
        std::cout << "TestBaseFunc7 is option2  " << option2 << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> TestBaseFunc8(float option1, bool option2)
    {
        if (option2) {
            std::cout << "TestBaseFunc8 is option1  " << option1 << std::endl;
            std::cout << "TestBaseFunc8 is option2  " << option2 << std::endl;
        } else {
            std::cout << "TestBaseFunc8 is option1  " << option1 << std::endl;
            std::cout << "TestBaseFunc8 is option2  " << option2 << std::endl;
        }
        return {};
    }

    ::taihe::expected<void, ::taihe::error> TestBaseFunc9(float option1, string_view option2)
    {
        std::cout << "TestBaseFunc9 is option1  " << option1 << std::endl;
        std::cout << "TestBaseFunc9 is option2  " << option2 << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> TestBaseFunc10(double option1, string_view option2)
    {
        std::cout << "TestBaseFunc10 is option1  " << option1 << std::endl;
        std::cout << "TestBaseFunc10 is option2  " << option2 << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> TestBaseFunc11(double option1, bool option2)
    {
        if (option1) {
            std::cout << "TestBaseFunc11 is option1  " << option1 << std::endl;
            std::cout << "TestBaseFunc11 is option2  " << option2 << std::endl;
        } else {
            std::cout << "TestBaseFunc11 is option1  " << option1 << std::endl;
            std::cout << "TestBaseFunc11 is option2  " << option2 << std::endl;
        }
        return {};
    }

    ::taihe::expected<void, ::taihe::error> TestBaseFunc12(optional_view<int32_t> option1,
                                                           optional_view<int64_t> option2)
    {
        if (option1) {
            std::cout << *option1 << std::endl;
        } else if (option2) {
            std::cout << *option2 << std::endl;
        } else {
            std::cout << "Null" << std::endl;
        }
        return {};
    }

    ::taihe::expected<void, ::taihe::error> TestBaseFunc13(optional_view<float> option1, optional_view<double> option2)
    {
        if (option1) {
            std::cout << *option1 << std::endl;
        } else if (option2) {
            std::cout << *option2 << std::endl;
        } else {
            std::cout << "Null" << std::endl;
        }
        return {};
    }

    ::taihe::expected<void, ::taihe::error> TestBaseFunc14(optional_view<string> option1, optional_view<bool> option2)
    {
        if (option1) {
            std::cout << *option1 << std::endl;
        } else if (option2) {
            std::cout << *option2 << std::endl;
        } else {
            std::cout << "Null" << std::endl;
        }
        return {};
    }

    ::taihe::expected<void, ::taihe::error> TestBaseFunc15(optional_view<int16_t> option1,
                                                           optional_view<int64_t> option2)
    {
        if (option1) {
            std::cout << *option1 << std::endl;
        } else if (option2) {
            std::cout << *option2 << std::endl;
        } else {
            std::cout << "Null" << std::endl;
        }
        return {};
    }

    ::taihe::expected<void, ::taihe::error> TestBaseFunc16(int8_t option1, int16_t option2)
    {
        std::cout << "TestBaseFunc16 is option1  " << static_cast<int>(option1) << std::endl;
        std::cout << "TestBaseFunc16 is option2  " << static_cast<int>(option2) << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> TestBaseFunc17(array_view<int32_t> option1, array_view<int8_t> option2)
    {
        // 输出 option1 的内容
        std::cout << "TestBaseFunc17 option1: ";
        for (int32_t value : option1) {
            std::cout << value << " ";
        }
        std::cout << std::endl;

        // 输出 option2 的内容
        std::cout << "TestBaseFunc17 option2: ";
        for (int8_t value : option2) {
            std::cout << (int)value << " ";
        }
        std::cout << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> TestBaseFunc18(array_view<int16_t> option1, array_view<int64_t> option2)
    {
        // 输出 option1 的内容
        std::cout << "TestBaseFunc18 option1: ";
        for (int16_t value : option1) {
            std::cout << value << " ";
        }
        std::cout << std::endl;

        // 输出 option2 的内容
        std::cout << "TestBaseFunc18 option2: ";
        for (int64_t value : option2) {
            std::cout << value << " ";
        }
        std::cout << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> TestBaseFunc19(array_view<float> option1, array_view<double> option2)
    {
        // 输出 option1 的内容
        std::cout << "TestBaseFunc19 option1: ";
        for (float value : option1) {
            std::cout << value << " ";
        }
        std::cout << std::endl;

        // 输出 option2 的内容
        std::cout << "TestBaseFunc19 option2: ";
        // 位小数
        for (double value : option2) {
            std::cout << value << " ";
        }
        std::cout << std::endl;
        return {};
    }

    ::taihe::expected<void, ::taihe::error> TestBaseFunc20(array_view<bool> option1, array_view<string> option2)
    {
        // 输出 option1 的内容
        std::cout << "TestBaseFunc20 option1: ";
        for (bool value : option1) {
            std::cout << value << " ";
        }
        std::cout << std::endl;

        // 输出 option2 的内容
        std::cout << "TestBaseFunc20 option2: ";
        for (string value : option2) {
            std::cout << value << " ";
        }
        std::cout << std::endl;
        return {};
    }
};

class PrimitivesBooleanClass {
public:
};

class PrimitivesBoolean {
    int testInt_65535_ {65535};

public:
    ::taihe::expected<void, ::taihe::error> TestBaseBoolFunc1(bool option1)
    {
        if (option1) {
            std::cout << "TestBaseBoolFunc1 is true " << option1 << std::endl;
        } else {
            std::cout << "TestBaseBoolFunc1 is false  " << option1 << std::endl;
        }
        return {};
    }

    ::taihe::expected<int32_t, ::taihe::error> TestBaseBoolFunc2(bool option1)
    {
        if (option1) {
            return testInt_65535_;
        } else {
            return 0;
        }
    }

    ::taihe::expected<bool, ::taihe::error> TestBaseBoolFunc3(bool option1)
    {
        if (option1) {
            return false;
        } else {
            return true;
        }
    }

    ::taihe::expected<bool, ::taihe::error> TestBaseBoolFunc4(optional_view<bool> option1)
    {
        if (option1) {
            return false;
        } else {
            return true;
        }
    }

    ::taihe::expected<bool, ::taihe::error> TestBaseBoolFunc5(bool option1)
    {
        if (option1) {
            return true;
        } else {
            return false;
        }
    }

    ::taihe::expected<bool, ::taihe::error> TestBaseBoolFunc7(map_view<string, bool> option1)
    {
        for (auto const &pair : option1) {
            if (pair.second) {
                return false;
            }
        }
        return true;
    }

    ::taihe::expected<bool, ::taihe::error> getBoolTest()
    {
        return true;
    }
};

class PrimitivesInteger {
public:
    ::taihe::expected<int8_t, ::taihe::error> TestBaseIntegerFunc1(int8_t option1)
    {
        if (option1 == -1) {
            return ::taihe::unexpected<::taihe::error>(
                ::taihe::error("out of range The i8 maximum value is 127 and minnum values is -128"));
        }
        return option1 + 1;
    }

    ::taihe::expected<int8_t, ::taihe::error> TestBaseIntegerFunc2(int8_t option1, int16_t option2)
    {
        if (option1 == -1) {
            return ::taihe::unexpected<::taihe::error>(
                ::taihe::error("out of range The i8 maximum value is 127 and minnum values is -128"));
        }
        if (option2 == -1) {
            return ::taihe::unexpected<::taihe::error>(
                ::taihe::error("out of range The i16 maximum value is 32767 and minnum values is -32768"));
        }
        return option1 + option2;
    }

    ::taihe::expected<void, ::taihe::error> TestBaseIntegerFunc3(int8_t option1, int16_t option2)
    {
        std::cout << "TestBaseIntegerFunc3 is option1  " << static_cast<int>(option1) << std::endl;
        std::cout << "TestBaseIntegerFunc3 is option2  " << option2 << std::endl;
        return {};
    }

    ::taihe::expected<int16_t, ::taihe::error> TestBaseIntegerFunc4(int8_t option1, int16_t option2)
    {
        return option1 + option2;
    }

    ::taihe::expected<int8_t, ::taihe::error> TestBaseIntegerFunc5(int8_t option1, int32_t option2)
    {
        return option1 + option2;
    }

    ::taihe::expected<int32_t, ::taihe::error> TestBaseIntegerFunc6(int8_t option1, int32_t option2)
    {
        return option1 + option2;
    }

    ::taihe::expected<void, ::taihe::error> TestBaseIntegerFunc7(int8_t option1, int32_t option2)
    {
        if (option2 == -1) {
            return ::taihe::unexpected<::taihe::error>(
                ::taihe::error("out of range The i32 maximum value is 2147483647 and minnum values is -2147483648"));
        }
        std::cout << "TestBaseIntegerFunc7 is option1  " << static_cast<int>(option1) << std::endl;
        std::cout << "TestBaseIntegerFunc7 is option2  " << option2 << std::endl;
        return {};
    }

    ::taihe::expected<int64_t, ::taihe::error> TestBaseIntegerFunc8(int8_t option1, int64_t option2)
    {
        if (option2 == -1) {
            return ::taihe::unexpected<::taihe::error>(::taihe::error(
                "out of range The i64 maximum value is 9223372036854775807 and minnum values is -9223372036854775808"));
        }
        return option2 - option1;
    }

    ::taihe::expected<int8_t, ::taihe::error> TestBaseIntegerFunc9(int8_t option1, int64_t option2)
    {
        if (option1 > INT8_MAX || option1 < INT8_MIN) {
            return ::taihe::unexpected<::taihe::error>(
                ::taihe::error("out of range The i8 maximum value is 127 and minnum values is -128"));
        }
        if (option2 > INT64_MAX || option2 < INT64_MIN) {
            return ::taihe::unexpected<::taihe::error>(::taihe::error(
                "out of range The i64 maximum value is 9223372036854775807 and minnum values is -9223372036854775808"));
        }
        return option2 - option1;
    }

    ::taihe::expected<float, ::taihe::error> TestBaseIntegerFunc10(int8_t option1, float option2)
    {
        return option1 + option2;
    }

    ::taihe::expected<int8_t, ::taihe::error> TestBaseIntegerFunc11(int8_t option1, float option2)
    {
        return option1 + option2;
    }

    ::taihe::expected<double, ::taihe::error> TestBaseIntegerFunc12(int8_t option1, double option2)
    {
        return option1 + option2;
    }

    ::taihe::expected<int8_t, ::taihe::error> TestBaseIntegerFunc13(int8_t option1, int64_t option2)
    {
        return option1 + option2;
    }

    ::taihe::expected<string, ::taihe::error> TestBaseIntegerFunc14(int8_t option1, string_view option2)
    {
        if (option2 == "TestBaseIntegerFunc14") {
            return std::string(option2) + std::to_string(option1);
        } else {
            return std::string(option2);
        }
    }

    ::taihe::expected<int8_t, ::taihe::error> TestBaseIntegerFunc15(int8_t option1, string_view option2)
    {
        if (option2 == "TestBaseIntegerFunc15") {
            return option1 + testInt_add10_;
        } else {
            return option1;
        }
    }

    ::taihe::expected<bool, ::taihe::error> TestBaseIntegerFunc16(int8_t option1, bool option2)
    {
        if (option2) {
            return true;
        } else {
            return false;
        }
    }

    ::taihe::expected<int8_t, ::taihe::error> TestBaseIntegerFunc17(int8_t option1, bool option2)
    {
        if (option2) {
            return option1 + 1;
        } else {
            return option1;
        }
    }

    ::taihe::expected<int16_t, ::taihe::error> TestBaseIntegerFunc18(int16_t option1)
    {
        // 检查结果是否超出 int16_t 的范围
        int32_t result = static_cast<int32_t>(option1) * testInt_add10_;  // 使用 int32_t 避免溢出
        if (result > INT16_MAX || result < INT16_MIN) {
            return ::taihe::unexpected<::taihe::error>(
                ::taihe::error("TestBaseIntegerFunc18: result exceeds int16_t range"));
        }
        // 返回结果
        return static_cast<int16_t>(result);
    }

    ::taihe::expected<void, ::taihe::error> TestBaseIntegerFunc19(int16_t option1)
    {
        std::cout << "TestBaseIntegerFunc19 is option1  " << option1 << std::endl;
        return {};
    }

    ::taihe::expected<int16_t, ::taihe::error> TestBaseIntegerFunc20(int16_t option1, int32_t option2)
    {
        // 检查结果是否超出 int16_t 的范围
        int32_t result = static_cast<int32_t>(option1) + option2;  // 使用 int32_t 避免溢出
        if (result > INT16_MAX || result < INT16_MIN) {
            return ::taihe::unexpected<::taihe::error>(
                ::taihe::error("TestBaseIntegerFunc20: result exceeds int16_t range"));
        }
        // 返回结果
        return static_cast<int16_t>(result);
    }

    ::taihe::expected<int16_t, ::taihe::error> TestBaseIntegerFunc21(int16_t option1, int64_t option2)
    {
        // 检查结果是否超出 int16_t 的范围
        int64_t result = static_cast<int64_t>(option1) + option2;
        if (result > INT16_MAX || result < INT16_MIN) {
            return ::taihe::unexpected<::taihe::error>(
                ::taihe::error("TestBaseIntegerFunc21: result exceeds int16_t range"));
        }
        // 返回结果
        return static_cast<int16_t>(result);
    }

    ::taihe::expected<int32_t, ::taihe::error> TestBaseIntegerFunc22(int32_t option1)
    {
        // 检查结果是否超出 int32_t 的范围
        int64_t result = static_cast<int32_t>(option1) * 100;
        if (result > INT32_MAX || result < INT32_MIN) {
            return ::taihe::unexpected<::taihe::error>(
                ::taihe::error("TestBaseIntegerFunc22: result exceeds int32_t range"));
        }
        // 返回结果
        return static_cast<int32_t>(result);
    }

    ::taihe::expected<void, ::taihe::error> TestBaseIntegerFunc23(int32_t option1)
    {
        if (option1 > INT32_MAX || option1 < INT32_MIN) {
            return ::taihe::unexpected<::taihe::error>(
                ::taihe::error("TestBaseIntegerFunc23: result exceeds int32_t range"));
        }
        std::cout << "TestBaseIntegerFunc23 is option1  " << option1 << std::endl;
        return {};
    }

    ::taihe::expected<int32_t, ::taihe::error> TestBaseIntegerFunc24(int32_t option1, int64_t option2)
    {
        // 检查结果是否超出 int32_t 的范围
        int64_t result = static_cast<int64_t>(option1) + option2;
        if (result > INT32_MAX || result < INT32_MIN) {
            return ::taihe::unexpected<::taihe::error>(
                ::taihe::error("TestBaseIntegerFunc24: result exceeds int32_t range"));
        }
        // 返回结果
        return static_cast<int32_t>(result);
    }

    ::taihe::expected<int32_t, ::taihe::error> TestBaseIntegerFunc25(int32_t option1, int8_t option2)
    {
        // 检查结果是否超出 int32_t 的范围
        int32_t result = static_cast<int32_t>(option2) + option1;
        if (result > INT32_MAX || result < INT32_MIN) {
            return ::taihe::unexpected<::taihe::error>(
                ::taihe::error("TestBaseIntegerFunc25: result exceeds int32_t range"));
        }
        // 返回结果
        return static_cast<int32_t>(result);
    }

    ::taihe::expected<int64_t, ::taihe::error> TestBaseIntegerFunc26(int64_t option1)
    {
        // 检查结果是否超出 int32_t 的范围
        int64_t result = option1 * 100;
        if (result > INT64_MAX || result < INT64_MIN) {
            return ::taihe::unexpected<::taihe::error>(
                ::taihe::error("TestBaseIntegerFunc25: result exceeds int64_t range"));
        }
        // 返回结果
        return static_cast<int64_t>(result);
    }

    ::taihe::expected<void, ::taihe::error> TestBaseIntegerFunc27(int64_t option1)
    {
        std::cout << "TestBaseIntegerFunc27 is option1  " << option1 << std::endl;
        return {};
    }

    ::taihe::expected<string, ::taihe::error> TestBaseIntegerFunc28(int64_t option1, string_view option2)
    {
        if (option2 == "TestBaseIntegerFunc28") {
            return std::string(option2) + std::to_string(option1);
        } else {
            return std::string(option2);
        }
    }

    ::taihe::expected<int64_t, ::taihe::error> TestBaseIntegerFunc29(int64_t option1, string_view option2)
    {
        if (option2 == "TestBaseIntegerFunc29") {
            int64_t result = option1 * testInt_add10_;
            if (result > INT64_MAX || result < INT64_MIN) {
                return ::taihe::unexpected<::taihe::error>(
                    ::taihe::error("TestBaseIntegerFunc29: result exceeds int32_t range"));
            }
            // 返回结果
            return static_cast<int64_t>(result);
        } else {
            return option1;
        }
    }

    ::taihe::expected<float, ::taihe::error> TestBaseIntegerFunc30(float option1)
    {
        return option1 + 1.0;
    }

    ::taihe::expected<void, ::taihe::error> TestBaseIntegerFunc31(float option1)
    {
        std::cout << std::fixed << std::setprecision(6);  // float 保留 6 位小数
        std::cout << "TestBaseIntegerFunc31 is option1  " << option1 << std::endl;
        return {};
    }

    ::taihe::expected<float, ::taihe::error> TestBaseIntegerFunc32(float option1, double option2)
    {
        return option1 + option2;
    }

    ::taihe::expected<double, ::taihe::error> TestBaseIntegerFunc33(float option1, double option2)
    {
        double result = static_cast<double>(option1) + option2;
        // 打印调试信息，保留 6 位小数
        std::cout << std::fixed << std::setprecision(6);
        std::cout << "Debug: option1 = " << option1 << ", option2 = " << option2 << ", result = " << result
                  << std::endl;
        return result;
    }

    ::taihe::expected<double, ::taihe::error> TestBaseIntegerFunc34(double option1)
    {
        return option1 + 1;
    }

    ::taihe::expected<void, ::taihe::error> TestBaseIntegerFunc35(double option1)
    {
        std::cout << std::fixed << std::setprecision(testInt_add15_);  // float 保留 6 位小数
        std::cout << "TestBaseIntegerFunc35 is option1  " << option1 << std::endl;
        return {};
    }

    ::taihe::expected<int8_t, ::taihe::error> getI8testattribute()
    {
        return INT8_MAX;
    }

    ::taihe::expected<int16_t, ::taihe::error> getI16testattribute()
    {
        return INT16_MIN;
    }

    ::taihe::expected<int32_t, ::taihe::error> getI32testattribute()
    {
        return INT32_MAX;
    }

    ::taihe::expected<int64_t, ::taihe::error> getI64testattribute()
    {
        return INT64_MAX;
    }

    ::taihe::expected<float, ::taihe::error> getf32testattribute()
    {
        float const getf32TestAttributeValue = 3.14;
        return getf32TestAttributeValue;
    }

    ::taihe::expected<double, ::taihe::error> getf64testattribute()
    {
        double const getf64TestAttributeValue = 123.45678;
        return getf64TestAttributeValue;
    }
};

static ::taihe::expected<void, ::taihe::error> parseOption(::primitives_test::Foo const &opt)
{
    std::cout << "num: " << opt.testNum << std::endl;
    std::cout << "str: " << opt.testStr << std::endl;
    return {};
}

::taihe::expected<int32_t, ::taihe::error> Multiply(int32_t a, int32_t b)
{
    return a * b;
}

::taihe::expected<bool, ::taihe::error> BaseCFunc(int32_t testBoolean)
{
    if (testBoolean == testInt_add10_) {
        return true;
    } else {
        return false;
    }
}

::taihe::expected<void, ::taihe::error> BaseAFunc(bool testBoolean)
{
    if (testBoolean) {
        std::cout << "testBoolean is true " << testBoolean << std::endl;
    } else {
        std::cout << "testBoolean is false  " << testBoolean << std::endl;
    }
    return {};
}

::taihe::expected<bool, ::taihe::error> BaseBFunc(bool testBoolean)
{
    if (testBoolean) {
        return false;
    } else {
        return true;
    }
}

::taihe::expected<bool, ::taihe::error> BaseDFunc(string_view testBoolean)
{
    if (testBoolean == "test123") {
        return true;
    } else {
        return false;
    }
}

::taihe::expected<string, ::taihe::error> BaseEFunc(::primitives_test::Foo const &b)
{
    parseOption(b);
    return "success";
}

::taihe::expected<string, ::taihe::error> BaseHFunc(int32_t a, int64_t b)
{
    int64_t sum = a + b;
    return std::to_string(sum);
}

::taihe::expected<string, ::taihe::error> BaseIFunc(double a, float b)
{
    double result = static_cast<double>(b) + a;
    std::cout << "BaseIFunc is true " << result << std::endl;
    return std::to_string(result);
}

::taihe::expected<float, ::taihe::error> BaseFunc1(float b)
{
    return b + 1.0;
}

::taihe::expected<void, ::taihe::error> BaseFunc2(float b)
{
    if (b == testFloat_1_) {
        std::cout << "BaseFunc2 is true " << b << std::endl;
    } else {
        std::cout << "BaseFunc2 is false  " << b << std::endl;
    }
    return {};
}

::taihe::expected<double, ::taihe::error> BaseFunc3(float a, double b)
{
    return static_cast<double>(a) + b;
}

::taihe::expected<double, ::taihe::error> BaseFunc4(double b)
{
    return b + 1.0;
}

::taihe::expected<void, ::taihe::error> BaseFunc5(double b)
{
    if (b == testDouble_2_) {
        std::cout << "BaseFunc5 is true " << b << std::endl;
    } else {
        std::cout << "BaseFunc5 is false  " << b << std::endl;
    }
    return {};
}

::taihe::expected<void, ::taihe::error> BaseFunc6(string_view a)
{
    if (a == "TestBaseFunc6") {
        std::cout << "BaseFunc6 is true " << a << std::endl;
    } else {
        std::cout << "BaseFunc6 is false  " << a << std::endl;
    }
    return {};
}

::taihe::expected<string, ::taihe::error> BaseFunc7(string_view a)
{
    if (a == "TestbaseFunc7") {
        return std::string(a);  // 返回 a
    } else {
        return std::string(a) + "false";  // 返回 a + "false";
    }
}

::taihe::expected<string, ::taihe::error> BaseFunc8(string_view a, int32_t b)
{
    if (a == "TestBaseFunc8") {
        return std::string(a) + std::to_string(b);  // 返回 a + b（b 转换为字符串）
    } else {
        return std::string(a);  // 返回 a
    }
}

::taihe::expected<void, ::taihe::error> BaseFunc9(string_view a, int32_t b, int64_t c, bool d, float e)
{
    if (a == "TestBaseFunc9") {
        std::cout << "str: " << a << std::endl;
    } else if (b == testInt_add32_) {
        std::cout << "int32: " << b << std::endl;
    } else if (c == INT64_MAX) {
        std::cout << "int64: " << c << std::endl;
    } else if (d) {
        std::cout << "boolean: " << d << std::endl;
    } else if (e == testDouble_1_) {
        std::cout << "testFloat: " << e << std::endl;
    } else {
        std::cout << "testError: " << std::endl;
    }
    return {};
}

::taihe::expected<void, ::taihe::error> BaseFunc10()
{
    std::cout << "BaseFunc10 is true " << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> BaseFunc11(int32_t a, bool b)
{
    if (b) {
        std::cout << "BaseFunc11 is a  " << a << std::endl;
        std::cout << "BaseFunc11 is b  " << b << std::endl;
    } else {
        std::cout << "BaseFunc11 is a  " << a << std::endl;
        std::cout << "BaseFunc11 is b  " << b << std::endl;
    }
    return {};
}

::taihe::expected<void, ::taihe::error> BaseFunc12(int32_t a, int64_t b)
{
    std::cout << "BaseFunc12 is a  " << a << std::endl;
    std::cout << "BaseFunc12 is b  " << b << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> BaseFunc13(int32_t a, string_view b)
{
    std::cout << "BaseFunc13 is a  " << a << std::endl;
    std::cout << "BaseFunc13 is b  " << b << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> BaseFunc14(int64_t a, bool b)
{
    if (b) {
        std::cout << "BaseFunc14 is a  " << a << std::endl;
        std::cout << "BaseFunc14 is b  " << b << std::endl;
    } else {
        std::cout << "BaseFunc14 is a  " << a << std::endl;
        std::cout << "BaseFunc14 is b  " << b << std::endl;
    }
    return {};
}

::taihe::expected<void, ::taihe::error> BaseFunc15(int64_t a, float b)
{
    std::cout << "BaseFunc15 is a  " << a << std::endl;
    std::cout << "BaseFunc15 is b  " << b << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> BaseFunc16(int64_t a, double b)
{
    std::cout << "BaseFunc16 is a  " << a << std::endl;
    std::cout << "BaseFunc16 is b  " << b << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> BaseFunc17(float a, bool b)
{
    if (b) {
        std::cout << "BaseFunc17 is a  " << a << std::endl;
        std::cout << "BaseFunc17 is b  " << b << std::endl;
    } else {
        std::cout << "BaseFunc17 is a  " << a << std::endl;
        std::cout << "BaseFunc17 is b  " << b << std::endl;
    }
    return {};
}

::taihe::expected<void, ::taihe::error> BaseFunc18(float a, string_view b)
{
    std::cout << "BaseFunc18 is a  " << a << std::endl;
    std::cout << "BaseFunc18 is b  " << b << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> BaseFunc19(double a, string_view b)
{
    std::cout << "BaseFunc19 is a  " << a << std::endl;
    std::cout << "BaseFunc19 is b  " << b << std::endl;
    return {};
}

::taihe::expected<void, ::taihe::error> BaseFunc20(double a, bool b)
{
    if (b) {
        std::cout << "BaseFunc20 is a  " << a << std::endl;
        std::cout << "BaseFunc20 is b  " << b << std::endl;
    } else {
        std::cout << "BaseFunc20 is a  " << a << std::endl;
        std::cout << "BaseFunc20 is b  " << b << std::endl;
    }
    return {};
}

::taihe::expected<void, ::taihe::error> BaseFunc21(optional_view<int32_t> option1, optional_view<int64_t> option2)
{
    if (option1) {
        std::cout << *option1 << std::endl;
    } else if (option2) {
        std::cout << *option2 << std::endl;
    } else {
        std::cout << "Null" << std::endl;
    }
    return {};
}

::taihe::expected<void, ::taihe::error> BaseFunc22(optional_view<float> option1, optional_view<double> option2)
{
    if (option1) {
        std::cout << *option1 << std::endl;
    } else if (option2) {
        std::cout << *option2 << std::endl;
    } else {
        std::cout << "Null" << std::endl;
    }
    return {};
}

::taihe::expected<void, ::taihe::error> BaseFunc23(optional_view<string> option1, optional_view<bool> option2)
{
    if (option1) {
        std::cout << *option1 << std::endl;
    } else if (option2) {
        std::cout << *option2 << std::endl;
    } else {
        std::cout << "Null" << std::endl;
    }
    return {};
}

::taihe::expected<void, ::taihe::error> BaseFunc24(optional_view<int16_t> option1, optional_view<int64_t> option2)
{
    if (option1) {
        std::cout << *option1 << std::endl;
    } else if (option2) {
        std::cout << *option2 << std::endl;
    } else {
        std::cout << "Null" << std::endl;
    }
    return {};
}

::taihe::expected<::primitives_test::PrimitivesVoid, ::taihe::error> get_interface()
{
    return make_holder<PrimitivesVoid, ::primitives_test::PrimitivesVoid>();
}

::taihe::expected<::primitives_test::PrimitivesBoolean, ::taihe::error> get_interface_bool()
{
    return make_holder<PrimitivesBoolean, ::primitives_test::PrimitivesBoolean>();
}

::taihe::expected<bool, ::taihe::error> TestBaseBoolFunc6()
{
    return false;
}

::taihe::expected<::primitives_test::PrimitivesInteger, ::taihe::error> get_interface_interger()
{
    return make_holder<PrimitivesInteger, ::primitives_test::PrimitivesInteger>();
}

}  // namespace

// because these macros are auto-generate, lint will cause false positive.
TH_EXPORT_CPP_API_Multiply(Multiply);
TH_EXPORT_CPP_API_BaseCFunc(BaseCFunc);
TH_EXPORT_CPP_API_BaseAFunc(BaseAFunc);
TH_EXPORT_CPP_API_BaseBFunc(BaseBFunc);
TH_EXPORT_CPP_API_BaseDFunc(BaseDFunc);
TH_EXPORT_CPP_API_BaseEFunc(BaseEFunc);
TH_EXPORT_CPP_API_BaseHFunc(BaseHFunc);
TH_EXPORT_CPP_API_BaseIFunc(BaseIFunc);
TH_EXPORT_CPP_API_BaseFunc1(BaseFunc1);
TH_EXPORT_CPP_API_BaseFunc2(BaseFunc2);
TH_EXPORT_CPP_API_BaseFunc3(BaseFunc3);
TH_EXPORT_CPP_API_BaseFunc4(BaseFunc4);
TH_EXPORT_CPP_API_BaseFunc5(BaseFunc5);
TH_EXPORT_CPP_API_BaseFunc6(BaseFunc6);
TH_EXPORT_CPP_API_BaseFunc7(BaseFunc7);
TH_EXPORT_CPP_API_BaseFunc8(BaseFunc8);
TH_EXPORT_CPP_API_BaseFunc9(BaseFunc9);
TH_EXPORT_CPP_API_BaseFunc10(BaseFunc10);
TH_EXPORT_CPP_API_BaseFunc11(BaseFunc11);
TH_EXPORT_CPP_API_BaseFunc12(BaseFunc12);
TH_EXPORT_CPP_API_BaseFunc13(BaseFunc13);
TH_EXPORT_CPP_API_BaseFunc14(BaseFunc14);
TH_EXPORT_CPP_API_BaseFunc15(BaseFunc15);
TH_EXPORT_CPP_API_BaseFunc16(BaseFunc16);
TH_EXPORT_CPP_API_BaseFunc17(BaseFunc17);
TH_EXPORT_CPP_API_BaseFunc18(BaseFunc18);
TH_EXPORT_CPP_API_BaseFunc19(BaseFunc19);
TH_EXPORT_CPP_API_BaseFunc20(BaseFunc20);
TH_EXPORT_CPP_API_BaseFunc21(BaseFunc21);
TH_EXPORT_CPP_API_BaseFunc22(BaseFunc22);
TH_EXPORT_CPP_API_BaseFunc23(BaseFunc23);
TH_EXPORT_CPP_API_BaseFunc24(BaseFunc24);
TH_EXPORT_CPP_API_get_interface(get_interface);
TH_EXPORT_CPP_API_get_interface_bool(get_interface_bool);
TH_EXPORT_CPP_API_TestBaseBoolFunc6(TestBaseBoolFunc6);
TH_EXPORT_CPP_API_get_interface_interger(get_interface_interger);
// NOLINTEND
