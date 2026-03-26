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

#include "my_module_a.impl.hpp"
#include <iostream>
#include "my_module_a.proj.hpp"

namespace {
void baz()
{
    std::cout << "namespace: my_module_a, func: baz" << std::endl;
}
}  // namespace

TH_EXPORT_CPP_API_baz(baz);
// NOLINTEND
