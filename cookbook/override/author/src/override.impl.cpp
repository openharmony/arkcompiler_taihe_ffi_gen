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

#include "override.impl.hpp"

#include <iostream>

#include "override.UIAbility.proj.2.hpp"
using namespace taihe;

namespace {
class UIAbility {
public:
  void onForeground() {
    std::cout << "in cpp onForeground" << std::endl;
  }

  void onBackground() {
    std::cout << "in cpp onBackground" << std::endl;
  }
};

::override::UIAbility getUIAbility() {
  return make_holder<UIAbility, ::override::UIAbility>();
}

void useUIAbility(::override::weak::UIAbility a) {
  a->onForeground();
  a->onBackground();
}

void logLifecycle(string_view str) {
  std::cout << "[UIAbility]: " << str << std::endl;
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_getUIAbility(getUIAbility);
TH_EXPORT_CPP_API_useUIAbility(useUIAbility);
TH_EXPORT_CPP_API_logLifecycle(logLifecycle);
// NOLINTEND
