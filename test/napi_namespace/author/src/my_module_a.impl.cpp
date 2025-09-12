#include "my_module_a.impl.hpp"
#include <iostream>
#include "my_module_a.proj.hpp"

namespace {
void baz() {
  std::cout << "namespace: my_module_a, func: baz" << std::endl;
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_baz(baz);
// NOLINTEND
