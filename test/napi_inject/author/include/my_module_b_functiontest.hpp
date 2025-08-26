#include "taihe/string.hpp"

namespace {
::taihe::string concat_str(::taihe::string_view a) {
  return a + "_concat";
}

int32_t concat_i32(int32_t a) {
  return a + 10;
}
}  // namespace
