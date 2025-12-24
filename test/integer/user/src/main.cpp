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
#include <iostream>

#include "integer.arithmetic.user.hpp"
#include "integer.io.user.hpp"

using namespace integer;

int main()
{
    std::cout << "Please enter a 32-bit signed integer a: ";
    auto a = io::input_i32();
    std::cout << "Please enter a 32-bit signed integer b: ";
    auto b = io::input_i32();

    auto sum = arithmetic::add_i32(a, b);
    auto diff = arithmetic::sub_i32(a, b);
    auto prod = arithmetic::mul_i32(a, b);
    auto [quo, rem] = arithmetic::divmod_i32(a, b);

    std::cout << "a + b = ";
    io::output_i32(sum);
    std::cout << "a - b = ";
    io::output_i32(diff);
    std::cout << "a * b = ";
    io::output_i32(prod);
    std::cout << "a / b = ";
    io::output_i32(quo);
    std::cout << "a % b = ";
    io::output_i32(rem);
}
// NOLINTEND
