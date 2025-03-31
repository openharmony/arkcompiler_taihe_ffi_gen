#include "mate.foo.impl.hpp"

#include "mate.MateType.proj.1.hpp"
#include "nova.NovaType.proj.2.hpp"
#include "pura.PuraType.proj.0.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe;
namespace {
void testMate(::mate::MateType const& mate) {
  throw std::runtime_error("Function testMate Not implemented");
}
void testNova(::nova::weak::NovaType nova) {
  throw std::runtime_error("Function testNova Not implemented");
}
void testPura(::pura::PuraType pura) {
  throw std::runtime_error("Function testPura Not implemented");
}
}  // namespace
TH_EXPORT_CPP_API_testMate(testMate);
TH_EXPORT_CPP_API_testNova(testNova);
TH_EXPORT_CPP_API_testPura(testPura);
