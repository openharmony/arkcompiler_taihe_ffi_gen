#include "export_toplevel_func.impl.hpp"
#include <iostream>
#include "export_toplevel_func.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

namespace {
// To be implemented.

void toplevel_func() {
  std::cout << "Export default toplevel func" << std::endl;
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_toplevel_func(toplevel_func);
// NOLINTEND
