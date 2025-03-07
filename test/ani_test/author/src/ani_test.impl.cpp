#include "ani_test.impl.hpp"

#include <iostream>

taihe::core::string ohos_input_str() {
    std::string str;
    std::cin >> str;
    return taihe::core::string(str);
}

template <bool endl>
void ohos_print_str(taihe::core::string_view pstr) {
    if (endl) {
        std::cout << pstr.c_str() << std::endl;
    } else {
        std::cout << pstr.c_str() << std::flush;
    }
}

TH_EXPORT_CPP_API_input(ohos_input_str)
TH_EXPORT_CPP_API_print(ohos_print_str<false>)
TH_EXPORT_CPP_API_println(ohos_print_str<true>)

ani_test::StringPair ohos_split_str(taihe::core::string_view pstr, int32_t n) {
    int32_t l = pstr.size();
    if (n > l) {
        n = l;
    } else if (n + l < 0) {
        n = 0;
    } else if (n < 0) {
        n = n + l;
    }
    return {
        taihe::core::substr(pstr, 0, n),
        taihe::core::substr(pstr, n, l - n),
    };
}

taihe::core::string ohos_int_to_str(int32_t n) {
    return taihe::core::to_string(n);
}

int32_t ohos_str_to_int(taihe::core::string_view pstr) {
    return std::atoi(pstr.c_str());
}

TH_EXPORT_CPP_API_split(ohos_split_str)
TH_EXPORT_CPP_API_to_i32(ohos_str_to_int)
TH_EXPORT_CPP_API_from_i32(ohos_int_to_str)
