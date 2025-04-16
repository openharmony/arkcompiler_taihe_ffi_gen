#include "test5namespace5.impl.hpp"

#include "stdexcept"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {
void Funtest1(int32_t a, double b) {}
}  // namespace

// because these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_Funtest1(Funtest1);
// NOLINTEND
