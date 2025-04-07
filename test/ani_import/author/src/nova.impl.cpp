#include "nova.proj.hpp"
#include "nova.impl.hpp"
#include "taihe/runtime.hpp"
#include "stdexcept"

using namespace taihe;
using namespace nova;

namespace {
// To be implemented.

class NovaTypeImpl {
public:
    NovaTypeImpl() {
        // Don't forget to implement the constructor.
    }
};

void testBar(::mate::bar::BarType const& bar) {
    TH_THROW(std::runtime_error, "testBar not implemented");
}

void testPura(::pura::PuraType pura) {
    TH_THROW(std::runtime_error, "testPura not implemented");
}

void testNova(weak::NovaType nova) {
    TH_THROW(std::runtime_error, "testNova not implemented");
}
}  // namespace

TH_EXPORT_CPP_API_testBar(testBar);
TH_EXPORT_CPP_API_testPura(testPura);
TH_EXPORT_CPP_API_testNova(testNova);
