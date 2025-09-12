#include "my_module_a.impl.hpp"
#include <iostream>
#include "my_module_a.proj.hpp"

namespace {
void baz() {
  std::cout << "namespace: my_module_a, func: baz" << std::endl;
}

::taihe::string concat_str(::taihe::string_view a) {
  return a + "_concat";
}

int32_t concat_i32(int32_t a) {
  return a + 10;
}

}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_baz(baz);
TH_EXPORT_CPP_API_concat_str(concat_str);
TH_EXPORT_CPP_API_concat_i32(concat_i32);
// NOLINTEND
