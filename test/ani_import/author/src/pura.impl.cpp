#include "pura.impl.hpp"

#include "mate.bar.BarType.proj.1.hpp"
#include "nova.NovaType.proj.2.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
void testBar(::mate::bar::BarType const& bar) {
  throw std::runtime_error("Function testBar Not implemented");
}
void testNova(::nova::weak::NovaType nove) {
  throw std::runtime_error("Function testNova Not implemented");
}
}  // namespace
TH_EXPORT_CPP_API_testBar(testBar);
TH_EXPORT_CPP_API_testNova(testNova);
