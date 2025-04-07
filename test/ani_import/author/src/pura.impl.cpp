#include "pura.proj.hpp"
#include "pura.impl.hpp"
#include "taihe/runtime.hpp"
#include "stdexcept"

using namespace taihe;
using namespace pura;

namespace {
// To be implemented.

void testBar(::mate::bar::BarType const& bar) {
    TH_THROW(std::runtime_error, "testBar not implemented");
}

void testNova(::nova::weak::NovaType nove) {
    TH_THROW(std::runtime_error, "testNova not implemented");
}

void testMyStruct(::test::inner::MyStruct const& s) {
    TH_THROW(std::runtime_error, "testMyStruct not implemented");
}
}  // namespace

TH_EXPORT_CPP_API_testBar(testBar);
TH_EXPORT_CPP_API_testNova(testNova);
TH_EXPORT_CPP_API_testMyStruct(testMyStruct);
