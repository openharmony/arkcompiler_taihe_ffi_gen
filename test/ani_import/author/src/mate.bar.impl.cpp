#include "mate.bar.proj.hpp"
#include "mate.bar.impl.hpp"
#include "taihe/runtime.hpp"
#include "stdexcept"

using namespace taihe;
using namespace mate::bar;

namespace {
// To be implemented.

void testFoo(::mate::foo::FooType const& foo) {
    TH_THROW(std::runtime_error, "testFoo not implemented");
}
}  // namespace

TH_EXPORT_CPP_API_testFoo(testFoo);
