#include "pura.impl.hpp"
#include "pura.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace pura;

namespace {
// To be implemented.

void testBar(::mate::bar::BarType const &bar) {
  TH_THROW(std::runtime_error, "testBar not implemented");
}

void testNova(::nova::weak::NovaType nove) {
  TH_THROW(std::runtime_error, "testNova not implemented");
}

void testMyStruct(::test::inner::MyStruct const &s) {
  TH_THROW(std::runtime_error, "testMyStruct not implemented");
}
}  // namespace

// because these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_testBar(testBar);
TH_EXPORT_CPP_API_testNova(testNova);
TH_EXPORT_CPP_API_testMyStruct(testMyStruct);
// NOLINTEND
