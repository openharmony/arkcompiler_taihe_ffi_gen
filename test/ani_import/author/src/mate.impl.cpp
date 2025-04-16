#include "mate.impl.hpp"
#include "mate.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace mate;

namespace {
// To be implemented.

void testBar(bar::BarType const &bar) {
  TH_THROW(std::runtime_error, "testBar not implemented");
}
}  // namespace

TH_EXPORT_CPP_API_testBar(testBar);
