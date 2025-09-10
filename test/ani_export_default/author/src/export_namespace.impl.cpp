#include "export_namespace.impl.hpp"
#include <iostream>
#include "export_namespace.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

namespace {
// To be implemented.

void Bar() {
  std::cout << "Export Namespace Bar()" << std::endl;
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_Bar(Bar);
// NOLINTEND
