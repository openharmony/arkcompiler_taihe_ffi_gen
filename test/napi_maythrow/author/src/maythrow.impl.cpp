#include <iostream>
#include <maythrow.impl.hpp>

#include "taihe/napi_runtime.hpp"

namespace {
int32_t maythrow_impl(int32_t a) {
  if (a == 0) {
    ::taihe::set_error("some error happen");
    return -1;
  } else {
    int const tempnum = 10;
    return a + tempnum;
  }
}

maythrow::Data getDataMaythrow() {
  ::taihe::set_error("error in getDataMaythrow");
  return {
      taihe::string("C++ Object"),
      (float)1.0,
      {"data.obj", "file.txt"},
  };
}

void noReturnMaythrow() {
  std::cout << "C++ if has error before: " << ::taihe::has_error() << std::endl;
  ::taihe::set_error("error in noReturnMaythrow");
  std::cout << "C++ if has error after: " << ::taihe::has_error() << std::endl;
}

void noReturnTypeError() {
  ::taihe::set_type_error("noReturnTypeError", "TypeError");
}

void noReturnRangeError() {
  ::taihe::set_range_error("noReturnRangeError", "RangeError");
}
}  // namespace

// because these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_maythrow(maythrow_impl);
TH_EXPORT_CPP_API_getDataMaythrow(getDataMaythrow);
TH_EXPORT_CPP_API_noReturnMaythrow(noReturnMaythrow);
TH_EXPORT_CPP_API_noReturnTypeError(noReturnTypeError);
TH_EXPORT_CPP_API_noReturnRangeError(noReturnRangeError);
// NOLINTEND
