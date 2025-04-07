#include "mate.foo.impl.hpp"
#include "mate.foo.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;
using namespace mate::foo;

namespace {
// To be implemented.

void testMate(::mate::MateType const& mate) {
  TH_THROW(std::runtime_error, "testMate not implemented");
}

void testNova(::nova::weak::NovaType nova) {
  TH_THROW(std::runtime_error, "testNova not implemented");
}

void testPura(::pura::PuraType pura) {
  TH_THROW(std::runtime_error, "testPura not implemented");
}
}  // namespace

TH_EXPORT_CPP_API_testMate(testMate);
TH_EXPORT_CPP_API_testNova(testNova);
TH_EXPORT_CPP_API_testPura(testPura);
