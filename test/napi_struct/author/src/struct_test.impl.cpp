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

#include "struct_test.impl.hpp"
#include "struct_test.proj.hpp"

namespace {
::taihe::expected<int32_t, ::taihe::error> from_rgb(::struct_test::RGB const &rgb)
{
    return rgb.r + rgb.g + rgb.b;
}

::taihe::expected<::struct_test::RGB, ::taihe::error> to_rgb(int32_t a)
{
    ::struct_test::RGB rgb {a, a / 2, a / 4};
    return rgb;
}

::taihe::expected<double, ::taihe::error> from_color(::struct_test::Color const &color)
{
    if (color.flag) {
        constexpr int32_t i32_value100 = 100;
        return color.rgb.r + i32_value100;
    } else {
        constexpr int32_t i32_value1 = 1;
        return color.price + i32_value1;
    }
}

::taihe::expected<::struct_test::Color, ::taihe::error> to_color(::taihe::string_view a, bool b, double c,
                                                                 ::struct_test::RGB const &d)
{
    ::struct_test::Color color {a, b, c, d};
    return color;
}

::taihe::expected<::struct_test::Student, ::taihe::error> create_student()
{
    return ::struct_test::Student {"Mary", 15};
}

::taihe::expected<::struct_test::Student, ::taihe::error> process_student(::struct_test::Student const &a)
{
    return ::struct_test::Student {a.name + " student", a.age + 10};
}

::taihe::expected<::struct_test::Teacher, ::taihe::error> create_teacher()
{
    return ::struct_test::Teacher {"Rose", 25};
}

::taihe::expected<::struct_test::Teacher, ::taihe::error> process_teacher(::struct_test::Teacher const &a)
{
    return ::struct_test::Teacher {a.name + " teacher", a.age + 15};
}

::taihe::expected<::struct_test::G, ::taihe::error> process_g(::struct_test::G const &a)
{
    return ::struct_test::G {{a.f.f + 1}, a.g + 2};
}

::taihe::expected<::struct_test::H, ::taihe::error> process_h(::struct_test::H const &a)
{
    return ::struct_test::H {{{a.g.f.f + 1}, a.g.g + 2}, a.h + 3};
}

::taihe::expected<::struct_test::H, ::taihe::error> create_h(int32_t f, int32_t g, int32_t h)
{
    return ::struct_test::H {{{f}, g}, h};
}

::taihe::expected<::taihe::string, ::taihe::error> give_lessons()
{
    return "math";
}
}  // namespace

TH_EXPORT_CPP_API_from_rgb(from_rgb);
TH_EXPORT_CPP_API_to_rgb(to_rgb);
TH_EXPORT_CPP_API_from_color(from_color);
TH_EXPORT_CPP_API_to_color(to_color);
TH_EXPORT_CPP_API_create_student(create_student);
TH_EXPORT_CPP_API_process_student(process_student);
TH_EXPORT_CPP_API_create_teacher(create_teacher);
TH_EXPORT_CPP_API_process_teacher(process_teacher);
TH_EXPORT_CPP_API_process_g(process_g);
TH_EXPORT_CPP_API_process_h(process_h);
TH_EXPORT_CPP_API_create_h(create_h);
TH_EXPORT_CPP_API_give_lessons(give_lessons);
// NOLINTEND
