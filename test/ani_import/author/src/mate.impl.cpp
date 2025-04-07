#include "mate.proj.hpp"
#include "mate.impl.hpp"
#include "taihe/runtime.hpp"
#include "stdexcept"

using namespace taihe;
using namespace mate;

namespace {
// To be implemented.

void testBar(bar::BarType const& bar) {
    TH_THROW(std::runtime_error, "testBar not implemented");
}
}  // namespace

TH_EXPORT_CPP_API_testBar(testBar);
