#include "mate.impl.hpp"

#include "mate.bar.BarType.proj.1.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
void testBar(::mate::bar::BarType const& bar) {
  throw std::runtime_error("Function testBar Not implemented");
}
}  // namespace
TH_EXPORT_CPP_API_testBar(testBar);
