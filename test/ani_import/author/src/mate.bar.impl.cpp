#include "mate.bar.impl.hpp"

#include "mate.foo.FooType.proj.1.hpp"
#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
void testFoo(::mate::foo::FooType const& foo) {
  throw std::runtime_error("Function testFoo Not implemented");
}
}  // namespace
TH_EXPORT_CPP_API_testFoo(testFoo);
