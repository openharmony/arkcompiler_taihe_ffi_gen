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

#include "module1.foo.impl.hpp"
#include <iostream>
#include "module1.foo.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;

namespace {
void fooFunc()
{
    std::cout << "namespace: module1.foo, func: foo" << std::endl;
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_fooFunc(fooFunc);
// NOLINTEND
