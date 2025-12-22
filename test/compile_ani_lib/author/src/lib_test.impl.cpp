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

#include "lib_test.impl.hpp"
#include <iostream>
#include "lib_test.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

namespace {
// To be implemented.

class IfaceAImpl {
public:
  IfaceAImpl() {}

  void Foo() {
    std::cout << "IfaceA::Foo" << std::endl;
  }

  void Bar() {
    std::cout << "IfaceA::Bar" << std::endl;
  }
};

::lib_test::IfaceA MakeIfaceA() {
  // The parameters in the make_holder function should be of the same type
  // as the parameters in the constructor of the actual implementation class.
  return taihe::make_holder<IfaceAImpl, ::lib_test::IfaceA>();
}

void UseIfaceA(::lib_test::weak::IfaceA obj) {
  std::cout << "UseIfaceA" << std::endl;
  obj->Foo();
  obj->Bar();
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_MakeIfaceA(MakeIfaceA);
TH_EXPORT_CPP_API_UseIfaceA(UseIfaceA);
// NOLINTEND
