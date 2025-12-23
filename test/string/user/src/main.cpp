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

#include "string.io.user.hpp"
#include "string.op.user.hpp"

int main()
{
    string::io::print("Please input string a: ");
    auto a = string::io::input();
    string::io::print("Please input string b: ");
    auto b = string::io::input();

    auto a_b = string::op::concat(a, b);

    string::io::print("a + b = ");
    string::io::println(a_b);

    string::io::print("Please input a number n: ");
    auto n_str = string::io::input();

    int32_t n = string::op::to_i32(n_str);
    n_str = string::op::from_i32(n);

    string::io::print("n = ");
    string::io::println(n_str);

    auto [a_0, a_1] = string::op::split(a, n);
    auto [b_0, b_1] = string::op::split(b, n);

    string::io::print("a[:n] = ");
    string::io::println(a_0);
    string::io::print("a[n:] = ");
    string::io::println(a_1);
    string::io::print("b[:n] = ");
    string::io::println(b_0);
    string::io::print("b[n:] = ");
    string::io::println(b_1);
}
