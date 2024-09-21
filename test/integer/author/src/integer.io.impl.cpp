#include "integer.io.impl.hpp"

#include <iostream>

int32_t ohos_int_input() {
    int n;
    std::cin >> n;
    return n;
}

void ohos_int_output(int32_t n) {
    std::cout << n << std::endl;
}

TH_EXPORT_CPP_API_input_i32(ohos_int_input)
TH_EXPORT_CPP_API_output_i32(ohos_int_output)
