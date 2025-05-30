#include "opt_test.impl.hpp"
#include <iostream>
#include "opt_test.proj.hpp"

namespace {
void showOptionalInt(::taihe::optional_view<int32_t> x) {
  if (x) {
    std::cout << *x << std::endl;
  } else {
    std::cout << "Null" << std::endl;
  }
}

::taihe::optional<int32_t> makeOptionalInt(bool b) {
  if (b) {
    int const optionalMakeValue = 10;
    return ::taihe::optional<int32_t>::make(optionalMakeValue);
  } else {
    return ::taihe::optional<int32_t>(nullptr);
  }
}

}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_showOptionalInt(showOptionalInt);
TH_EXPORT_CPP_API_makeOptionalInt(makeOptionalInt);
// NOLINTEND
