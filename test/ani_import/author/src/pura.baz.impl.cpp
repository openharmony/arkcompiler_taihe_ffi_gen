#include "pura.baz.proj.hpp"
#include "pura.baz.impl.hpp"
#include "taihe/runtime.hpp"
#include "stdexcept"

using namespace taihe;
using namespace pura::baz;

namespace {
// To be implemented.

void testFoo(::mate::foo::FooType const& foo) {
    TH_THROW(std::runtime_error, "testFoo not implemented");
}

void testBaz(BazType const& baz) {
    TH_THROW(std::runtime_error, "testBaz not implemented");
}
}  // namespace

TH_EXPORT_CPP_API_testFoo(testFoo);
TH_EXPORT_CPP_API_testBaz(testBaz);
