#include <iostream>
#include <maythrow.impl.hpp>

#include "taihe/runtime.hpp"

int32_t maythrow_impl(int32_t a) {
  if (a == 0) {
    taihe::set_error("some error happen");
    return -1;
  } else {
    return a + 10;
  }
}

maythrow::Data getDataMaythrow() {
  taihe::set_error("error in getDataMaythrow");
  return {
      taihe::string("C++ Object"),
      (float)1.0,
      {"data.obj", "file.txt"},
  };
}

void noReturnMaythrow() {
  taihe::set_error("error in noReturnMaythrow");
}

TH_EXPORT_CPP_API_maythrow(maythrow_impl);
TH_EXPORT_CPP_API_getDataMaythrow(getDataMaythrow);
TH_EXPORT_CPP_API_noReturnMaythrow(noReturnMaythrow);
