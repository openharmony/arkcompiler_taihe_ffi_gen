#include "test5namespace5.impl.hpp"

#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {
void Funtest(::test5namespace5::MyStruct const &s) {}
}  // namespace

// because these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_Funtest(Funtest);
// NOLINTEND
