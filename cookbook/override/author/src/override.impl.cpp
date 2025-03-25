#include "override.impl.hpp"

#include <iostream>

#include "override.UIAbility.proj.2.hpp"
using namespace taihe::core;
namespace {
class UIAbility {
 public:
  void onForeground() { std::cout << "in cpp onForeground" << std::endl; }
  void onBackground() { std::cout << "in cpp onBackground" << std::endl; }
};
::override::UIAbility getUIAbility() {
  return make_holder<UIAbility, ::override::UIAbility>();
}
void useUIAbility(::override::weak::UIAbility a) {
  a->onForeground();
  a->onBackground();
}
}  // namespace
TH_EXPORT_CPP_API_getUIAbility(getUIAbility);
TH_EXPORT_CPP_API_useUIAbility(useUIAbility);
