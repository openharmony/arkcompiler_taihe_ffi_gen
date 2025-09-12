#include "string_test.impl.hpp"

taihe::string ohos_concat_str(taihe::string_view a, taihe::string_view b) {
  return a + b;
}

taihe::string ohos_int_to_str(int32_t n) {
  return taihe::to_string(n);
}

int32_t ohos_str_to_int(taihe::string_view pstr) {
  return std::atoi(pstr.c_str());
}

taihe::string ohos_show() {
  return "success";
}

int32_t add(int32_t a, int32_t b) {
  return a + b;
}

TH_EXPORT_CPP_API_concat(ohos_concat_str);
TH_EXPORT_CPP_API_to_i32(ohos_str_to_int);
TH_EXPORT_CPP_API_from_i32(ohos_int_to_str);
TH_EXPORT_CPP_API_show(ohos_show);
TH_EXPORT_CPP_API_add(add);
