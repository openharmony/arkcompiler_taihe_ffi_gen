#include "my_module_b.functiontest.impl.hpp"
#include "my_module_b.functiontest.proj.hpp"

namespace {
::taihe::string concat_str(::taihe::string_view a) {
  return a + "_concat";
}

int32_t concat_i32(int32_t a) {
  return a + 10;
}

}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_concat_str(concat_str);
TH_EXPORT_CPP_API_concat_i32(concat_i32);
// NOLINTEND
