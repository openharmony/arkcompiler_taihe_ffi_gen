#include <iostream>

#include "enum_test.Color.proj.0.hpp"
#include "enum_test.impl.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
::enum_test::Color nextEnum(::enum_test::Color color) {
  return (::enum_test::Color::key_t)(((int)color.get_key() + 1) % 3);
}
void showEnum(::enum_test::Color color) { std::cout << color << std::endl; }
}  // namespace
TH_EXPORT_CPP_API_nextEnum(nextEnum) TH_EXPORT_CPP_API_showEnum(showEnum)
