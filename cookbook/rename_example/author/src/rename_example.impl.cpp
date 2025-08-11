#include "rename_example.proj.hpp"
#include "rename_example.impl.hpp"
#include "taihe/runtime.hpp"
#include "stdexcept"


namespace {
// To be implemented.

int32_t oldFoo(int32_t a, int32_t b) {
    return a + b;
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_oldFoo(oldFoo);
// NOLINTEND
