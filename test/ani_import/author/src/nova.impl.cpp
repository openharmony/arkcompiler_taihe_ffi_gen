#include "nova.impl.hpp"

#include "mate.bar.BarType.proj.1.hpp"
#include "nova.NovaType.proj.2.hpp"
#include "pura.PuraType.proj.0.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
class NovaType {
 public:
};
void testBar(::mate::bar::BarType const& bar) {
  throw std::runtime_error("Function testBar Not implemented");
}
void testPura(::pura::PuraType pura) {
  throw std::runtime_error("Function testPura Not implemented");
}
void testNova(::nova::weak::NovaType nova) {
  throw std::runtime_error("Function testNova Not implemented");
}
}  // namespace
TH_EXPORT_CPP_API_testBar(testBar);
TH_EXPORT_CPP_API_testPura(testPura);
TH_EXPORT_CPP_API_testNova(testNova);
