#include "pura.baz.impl.hpp"

#include "mate.foo.FooType.proj.1.hpp"
#include "pura.baz.BazType.proj.1.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
void testFoo(::mate::foo::FooType const& foo) {
  throw std::runtime_error("Function testFoo Not implemented");
}
void testBaz(::pura::baz::BazType const& baz) {
  throw std::runtime_error("Function testBaz Not implemented");
}
}  // namespace
TH_EXPORT_CPP_API_testFoo(testFoo);
TH_EXPORT_CPP_API_testBaz(testBaz);
