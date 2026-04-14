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
#include "inner.impl.hpp"

#include "inner.Color.proj.1.hpp"
#include "inner.ErrorResponse.proj.1.hpp"
#include "inner.Mystruct.proj.1.hpp"
#include "inner.Test1.proj.2.hpp"
#include "inner.Test20.proj.2.hpp"
#include "inner.TestA.proj.2.hpp"
#include "inner.TestInterface.proj.2.hpp"
#include "inner.union_primitive.proj.1.hpp"
#include "stdexcept"
#include "taihe/array.hpp"
#include "taihe/map.hpp"
#include "taihe/string.hpp"

// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {
class TestInterface {
public:
    ::taihe::expected<void, ::taihe::error> Noparam_noreturn()
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Primitives_noreturn(int8_t a)
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Primitives_noreturn1(int16_t a)
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Primitives_noreturn2(int32_t a)
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Primitives_noreturn3(float a)
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Primitives_noreturn4(double a)
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Primitives_noreturn5(bool a)
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Primitives_noreturn6(string_view a)
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Primitives_noreturn7(int64_t a)
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Primitives_noreturn8(int8_t a)
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Primitives_noreturn9(int32_t a)
    {
        return {};
    }

    ::taihe::expected<int32_t, ::taihe::error> Primitives_return(int32_t a)
    {
        return 1;
    }

    ::taihe::expected<void, ::taihe::error> Containers_noreturn1(array_view<int8_t> a)
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Containers_noreturn3(array_view<uint8_t> a)
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Containers_noreturn2(::inner::union_primitive const &a)
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Containers_noreturn4(::inner::Color a)
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Containers_noreturn5(map_view<string, int32_t> a)
    {
        return {};
    }

    ::taihe::expected<string, ::taihe::error> Containers_return(::inner::union_primitive const &a)
    {
        return "containers_return";
    }

    ::taihe::expected<::inner::ErrorResponse, ::taihe::error> Func_ErrorResponse()
    {
        return ::inner::ErrorResponse {true, 10000, "test58"};
    }

    ::taihe::expected<void, ::taihe::error> OverloadFunc_i8(int8_t a, int8_t b)
    {
        return {};
    }

    ::taihe::expected<string, ::taihe::error> OverloadFunc_i16(array_view<int8_t> a, array_view<uint8_t> b)
    {
        return "overload array";
    }

    ::taihe::expected<void, ::taihe::error> OverloadFunc_i32()
    {
        return {};
    }

    ::taihe::expected<::inner::Mystruct, ::taihe::error> OverloadFunc_f32(::inner::Mystruct const &a)
    {
        return a;
    }

    int8_t i8 = -128;           // 范围: -128 到 127
    int16_t i16 = -32768;       // 16 位有符号整数，范围: -32,768 到 32,767
    int32_t i32 = -2147483648;  // 32 位有符号整数，范围: -2,147,483,648 到 2,147,483,647
    int64_t i64 = 1000;         // 64 位有符号整数，范围: -9,223,372,036,854,775,808 到
                                // 9,223,372,036,854,775,807

    // 浮点类型
    float f32 = 3.14159265f;         // 32 位单精度浮点，约 7 位有效数字
    double f64 = 3.141592653589793;  // 64 位双精度浮点，约 15 位有效数字

    // 其他类型
    string name_ {"String"};
    bool flag = true;  // 布尔类型，值: true 或 false

    ::taihe::expected<string, ::taihe::error> getName()
    {
        std::cout << __func__ << " " << name_ << std::endl;
        return name_;
    }

    ::taihe::expected<int8_t, ::taihe::error> geti8()
    {
        std::cout << __func__ << " " << (int)i8 << std::endl;
        return i8;
    }

    ::taihe::expected<int16_t, ::taihe::error> geti16()
    {
        std::cout << __func__ << " " << i16 << std::endl;
        return i16;
    }

    ::taihe::expected<int32_t, ::taihe::error> geti32()
    {
        std::cout << __func__ << " " << i32 << std::endl;
        return i32;
    }

    ::taihe::expected<int64_t, ::taihe::error> geti64()
    {
        std::cout << __func__ << " " << i64 << std::endl;
        return i64;
    }

    ::taihe::expected<float, ::taihe::error> getf32()
    {
        std::cout << __func__ << " " << f32 << std::endl;
        return f32;
    }

    ::taihe::expected<double, ::taihe::error> getf64()
    {
        std::cout << __func__ << " " << f64 << std::endl;
        return f64;
    }

    ::taihe::expected<bool, ::taihe::error> getbool()
    {
        std::cout << __func__ << " " << flag << std::endl;
        return flag;
    }

    ::taihe::expected<array<uint8_t>, ::taihe::error> getArraybuffer()
    {
        int const len = 5;
        int const member = 3;
        array<uint8_t> result = array<uint8_t>::make(len);
        std::fill(result.begin(), result.end(), member);
        return result;
    }

    ::taihe::expected<array<int8_t>, ::taihe::error> getArray()
    {
        int const len = 5;
        int const member = 3;
        array<int8_t> result = array<int8_t>::make(len);
        std::fill(result.begin(), result.end(), member);
        return result;
    }

    ::taihe::expected<::inner::union_primitive, ::taihe::error> getunion()
    {
        return ::inner::union_primitive::make_sValue("union string");
    }

    ::taihe::expected<map<string, int8_t>, ::taihe::error> getrecord()
    {
        map<string, int8_t> m;
        int const key1num = 1;
        int const key2num = 2;
        int const key3num = 3;
        m.emplace("key1", static_cast<int8_t>(key1num));
        m.emplace("key2", static_cast<int8_t>(key2num));
        m.emplace("key3", static_cast<int8_t>(key3num));
        return m;
    }

    ::taihe::expected<::inner::Color, ::taihe::error> getColorEnum()
    {
        return (::inner::Color::key_t)((int)1);
    }
};

class Test1 {
public:
    ::taihe::expected<void, ::taihe::error> Fun1()
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Fun2()
    {
        return {};
    }
};

class Test2 {
public:
    ::taihe::expected<void, ::taihe::error> Fun1()
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Fun2()
    {
        return {};
    }
};

class Test3 {
public:
    ::taihe::expected<void, ::taihe::error> Fun1()
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Fun2()
    {
        return {};
    }
};

class Test4 {
public:
    ::taihe::expected<void, ::taihe::error> Fun1()
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Fun2()
    {
        return {};
    }
};

class Test5 {
public:
    ::taihe::expected<void, ::taihe::error> Fun1()
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Fun2()
    {
        return {};
    }
};

class Test6 {
public:
    ::taihe::expected<void, ::taihe::error> Fun1()
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Fun2()
    {
        return {};
    }
};

class Test7 {
public:
    ::taihe::expected<void, ::taihe::error> Fun1()
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Fun2()
    {
        return {};
    }
};

class Test8 {
public:
    ::taihe::expected<void, ::taihe::error> Fun1()
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Fun2()
    {
        return {};
    }
};

class Test9 {
public:
    ::taihe::expected<void, ::taihe::error> Fun1()
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Fun2()
    {
        return {};
    }
};

class Test10 {
public:
    ::taihe::expected<void, ::taihe::error> Fun1()
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Fun2()
    {
        return {};
    }
};

class Test11 {
public:
    ::taihe::expected<void, ::taihe::error> Fun1()
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Fun2()
    {
        return {};
    }
};

class Test12 {
public:
    ::taihe::expected<void, ::taihe::error> Fun1()
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Fun2()
    {
        return {};
    }
};

class Test13 {
public:
    ::taihe::expected<void, ::taihe::error> Fun1()
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Fun2()
    {
        return {};
    }
};

class Test14 {
public:
    ::taihe::expected<void, ::taihe::error> Fun1()
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Fun2()
    {
        return {};
    }
};

class Test15 {
public:
    ::taihe::expected<void, ::taihe::error> Fun1()
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Fun2()
    {
        return {};
    }
};

class Test16 {
public:
    ::taihe::expected<void, ::taihe::error> Fun1()
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Fun2()
    {
        return {};
    }
};

class Test17 {
public:
    ::taihe::expected<void, ::taihe::error> Fun1()
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Fun2()
    {
        return {};
    }
};

class Test18 {
public:
    ::taihe::expected<void, ::taihe::error> Fun1()
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Fun2()
    {
        return {};
    }
};

class Test19 {
public:
    ::taihe::expected<void, ::taihe::error> Fun1()
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Fun2()
    {
        return {};
    }
};

class Test20 {
public:
    ::taihe::expected<void, ::taihe::error> Fun1()
    {
        return {};
    }

    ::taihe::expected<void, ::taihe::error> Fun2()
    {
        return {};
    }
};

class TestA {
public:
    ::taihe::expected<string, ::taihe::error> Fun1()
    {
        std::cout << "fun1" << std::endl;
        return "fun1";
    }
};

class TestB {
public:
    ::taihe::expected<string, ::taihe::error> Fun2()
    {
        std::cout << "IfaceB func_b" << std::endl;
        return "fun2";
    }

    ::taihe::expected<string, ::taihe::error> Fun1()
    {
        std::cout << "IfaceB func_a" << std::endl;
        return "fun1";
    }
};

class TestC {
public:
    ::taihe::expected<string, ::taihe::error> Fun3()
    {
        std::cout << "IfaceC func_c" << std::endl;
        return "fun3";
    }

    ::taihe::expected<string, ::taihe::error> Fun1()
    {
        std::cout << "IfaceC func_a" << std::endl;
        return "fun1";
    }
};

::taihe::expected<void, ::taihe::error> Primitives_noreturn(int32_t a, double b, bool c, string_view d, int8_t e)
{
    return {};
}

::taihe::expected<string, ::taihe::error> Primitives_return(int32_t a, double b, bool c, string_view d, int8_t e)
{
    return "primitives_return";
}

::taihe::expected<void, ::taihe::error> Containers_noreturn(array_view<int8_t> a, array_view<int16_t> b,
                                                            array_view<float> c, array_view<double> d,
                                                            ::inner::union_primitive const &e)
{
    return {};
}

::taihe::expected<string, ::taihe::error> Containers_return(array_view<int8_t> a, array_view<int16_t> b,
                                                            array_view<float> c, array_view<double> d,
                                                            ::inner::union_primitive const &e)
{
    return "containers_return";
}

::taihe::expected<void, ::taihe::error> Enum_noreturn(::inner::Color a, ::inner::Color b, ::inner::Color c,
                                                      ::inner::Color d, ::inner::Color e)
{
    return {};
}

::taihe::expected<string, ::taihe::error> Enum_return(::inner::Color a, ::inner::Color b, ::inner::Color c,
                                                      ::inner::Color d, ::inner::Color e)
{
    return "enum_return";
}

::taihe::expected<::inner::TestInterface, ::taihe::error> get_interface()
{
    return make_holder<TestInterface, ::inner::TestInterface>();
}

::taihe::expected<string, ::taihe::error> PrintTestInterfaceName(::inner::weak::TestInterface testiface)
{
    auto result = testiface->getName();
    if (result.has_value()) {
        auto name = result.value();
        std::cout << __func__ << ": " << name << std::endl;
        return name;
    }
    return "";
}

::taihe::expected<int8_t, ::taihe::error> PrintTestInterfaceNumberi8(::inner::weak::TestInterface testiface)
{
    auto result = testiface->geti8();
    if (result.has_value()) {
        auto name = result.value();
        std::cout << __func__ << ": " << (int)name << std::endl;
        return name;
    }
    return 0;
}

::taihe::expected<int16_t, ::taihe::error> PrintTestInterfaceNumberi16(::inner::weak::TestInterface testiface)
{
    auto result = testiface->geti16();
    if (result.has_value()) {
        auto name = result.value();
        std::cout << __func__ << ": " << name << std::endl;
        return name;
    }
    return 0;
}

::taihe::expected<int32_t, ::taihe::error> PrintTestInterfaceNumberi32(::inner::weak::TestInterface testiface)
{
    auto result = testiface->geti32();
    if (result.has_value()) {
        auto name = result.value();
        std::cout << __func__ << ": " << name << std::endl;
        return name;
    }
    return 0;
}

::taihe::expected<int64_t, ::taihe::error> PrintTestInterfaceNumberi64(::inner::weak::TestInterface testiface)
{
    auto result = testiface->geti64();
    if (result.has_value()) {
        auto name = result.value();
        std::cout << __func__ << ": " << name << std::endl;
        return name;
    }
    return 0;
}

::taihe::expected<float, ::taihe::error> PrintTestInterfaceNumberf32(::inner::weak::TestInterface testiface)
{
    auto result = testiface->getf32();
    if (result.has_value()) {
        auto name = result.value();
        std::cout << __func__ << ": " << name << std::endl;
        return name;
    }
    return 0.0f;
}

::taihe::expected<double, ::taihe::error> PrintTestInterfaceNumberf64(::inner::weak::TestInterface testiface)
{
    auto result = testiface->getf64();
    if (result.has_value()) {
        auto name = result.value();
        std::cout << __func__ << ": " << name << std::endl;
        return name;
    }
    return 0.0;
}

::taihe::expected<bool, ::taihe::error> PrintTestInterfacebool(::inner::weak::TestInterface testiface)
{
    auto result = testiface->getbool();
    if (result.has_value()) {
        auto name = result.value();
        std::cout << __func__ << ": " << name << std::endl;
        return name;
    }
    return false;
}

::taihe::expected<array<uint8_t>, ::taihe::error> PrintTestInterfaceArraybuffer(::inner::weak::TestInterface testiface)
{
    ::taihe::expected<array<uint8_t>, ::taihe::error> arr = testiface->getArraybuffer();
    if (arr.has_value()) {
        for (size_t i = 0; i < arr.value().size(); ++i) {
            std::cout << static_cast<int>(arr.value().data()[i]);
            if (i < arr.value().size() - 1) {
                std::cout << ", ";
            }
        }
    }
    return arr;
}

::taihe::expected<array<int8_t>, ::taihe::error> PrintTestInterfaceArray(::inner::weak::TestInterface testiface)
{
    ::taihe::expected<array<int8_t>, ::taihe::error> arr = testiface->getArray();
    if (arr.has_value()) {
        for (size_t i = 0; i < arr.value().size(); ++i) {
            std::cout << static_cast<int>(arr.value().data()[i]);
            if (i < arr.value().size() - 1) {
                std::cout << ", ";
            }
        }
    }
    return arr;
}

::taihe::expected<::inner::union_primitive, ::taihe::error> PrintTestInterfaceUnion(
    ::inner::weak::TestInterface testiface)
{
    return testiface->getunion();
}

::taihe::expected<map<string, int8_t>, ::taihe::error> PrintTestInterfaceRecord(::inner::weak::TestInterface testiface)
{
    ::taihe::expected<map<string, int8_t>, ::taihe::error> m = testiface->getrecord();
    if (m.has_value()) {
        for (auto const &[key, value] : m.value()) {
            std::cout << "Key: " << key << ", Value: " << static_cast<int>(value) << std::endl;
            // 注意：int8_t 需要转为 int 打印，否则会输出 ASCII 字符
        }
    }
    return m;
}

::taihe::expected<::inner::Color, ::taihe::error> PrintTestInterfaceEnum(::inner::weak::TestInterface testiface)
{
    ::taihe::expected<::inner::Color, ::taihe::error> c = testiface->getColorEnum();
    if (c.has_value()) {
        std::cout << "enum get_key " << (int)c.value().get_key() << std::endl;
    }
    return c;
}

::taihe::expected<::inner::Test1, ::taihe::error> get_interface_1()
{
    return make_holder<Test1, ::inner::Test1>();
}

::taihe::expected<::inner::Test20, ::taihe::error> get_interface_20()
{
    return make_holder<Test20, ::inner::Test20>();
}

::taihe::expected<::inner::TestA, ::taihe::error> get_interface_A()
{
    return make_holder<TestA, ::inner::TestA>();
}

::taihe::expected<::inner::TestB, ::taihe::error> get_interface_B()
{
    return make_holder<TestB, ::inner::TestB>();
}

::taihe::expected<::inner::TestC, ::taihe::error> get_interface_C()
{
    return make_holder<TestC, ::inner::TestC>();
}

}  // namespace

// because these macros are auto-generate, lint will cause false positive.
TH_EXPORT_CPP_API_Primitives_noreturn(Primitives_noreturn);
TH_EXPORT_CPP_API_Primitives_return(Primitives_return);
TH_EXPORT_CPP_API_Containers_noreturn(Containers_noreturn);
TH_EXPORT_CPP_API_Containers_return(Containers_return);
TH_EXPORT_CPP_API_Enum_noreturn(Enum_noreturn);
TH_EXPORT_CPP_API_Enum_return(Enum_return);
TH_EXPORT_CPP_API_get_interface(get_interface);
TH_EXPORT_CPP_API_PrintTestInterfaceName(PrintTestInterfaceName);
TH_EXPORT_CPP_API_PrintTestInterfaceNumberi8(PrintTestInterfaceNumberi8);
TH_EXPORT_CPP_API_PrintTestInterfaceNumberi16(PrintTestInterfaceNumberi16);
TH_EXPORT_CPP_API_PrintTestInterfaceNumberi32(PrintTestInterfaceNumberi32);
TH_EXPORT_CPP_API_PrintTestInterfaceNumberi64(PrintTestInterfaceNumberi64);
TH_EXPORT_CPP_API_PrintTestInterfaceNumberf32(PrintTestInterfaceNumberf32);
TH_EXPORT_CPP_API_PrintTestInterfaceNumberf64(PrintTestInterfaceNumberf64);
TH_EXPORT_CPP_API_PrintTestInterfacebool(PrintTestInterfacebool);
TH_EXPORT_CPP_API_PrintTestInterfaceArraybuffer(PrintTestInterfaceArraybuffer);
TH_EXPORT_CPP_API_PrintTestInterfaceArray(PrintTestInterfaceArray);
TH_EXPORT_CPP_API_PrintTestInterfaceUnion(PrintTestInterfaceUnion);
TH_EXPORT_CPP_API_PrintTestInterfaceRecord(PrintTestInterfaceRecord);
TH_EXPORT_CPP_API_PrintTestInterfaceEnum(PrintTestInterfaceEnum);
TH_EXPORT_CPP_API_get_interface_1(get_interface_1);
TH_EXPORT_CPP_API_get_interface_20(get_interface_20);
TH_EXPORT_CPP_API_get_interface_A(get_interface_A);
TH_EXPORT_CPP_API_get_interface_B(get_interface_B);
TH_EXPORT_CPP_API_get_interface_C(get_interface_C);
// NOLINTEND
