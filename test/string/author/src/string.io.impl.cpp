#include "string.io.impl.hpp"

#include <iostream>

taihe::string ohos_input_str() {
  std::string str;
  std::cin >> str;
  return taihe::string(str);
}

template<bool endl>
void ohos_print_str(taihe::string_view pstr) {
  if (endl) {
    std::cout << pstr.c_str() << std::endl;
  } else {
    std::cout << pstr.c_str() << std::flush;
  }
}

TH_EXPORT_CPP_API_input(ohos_input_str);
TH_EXPORT_CPP_API_print(ohos_print_str<false>);
TH_EXPORT_CPP_API_println(ohos_print_str<true>);
