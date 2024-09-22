#include "string.io.impl.hpp"

#include <iostream>

taihe::core::string ohos_input_str() {
    std::string str;
    std::cin >> str;
    return taihe::core::string(str);
}

template <bool endl>
void ohos_print_str(taihe::core::string const &tstr) {
    std::string_view str = tstr;
    if (endl) {
        std::cout << str << std::endl;
    } else {
        std::cout << str;
    }
}

TH_EXPORT_CPP_API_input(ohos_input_str)
TH_EXPORT_CPP_API_print(ohos_print_str<false>)
TH_EXPORT_CPP_API_println(ohos_print_str<true>)
