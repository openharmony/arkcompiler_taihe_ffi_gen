#include "string.io.impl.hpp"

#include <iostream>

taihe::core::string ohos_read_str() {
    std::string str;
    std::cin >> str;
    return taihe::core::string(str);
}

void ohos_write_str(taihe::core::param::string pstr) {
    taihe::core::string tstr = pstr;
    std::string_view str = tstr;
    std::cout << str << std::endl;
}

TH_EXPORT_CPP_API_input(ohos_read_str)
TH_EXPORT_CPP_API_output(ohos_write_str)
