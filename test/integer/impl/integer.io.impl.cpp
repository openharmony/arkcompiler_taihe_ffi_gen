#include "integer.io.impl.hpp"

#include <iostream>

namespace _impl::integer::io {
int32_t input_i32() {
    int n;
    std::cin >> n;
    return n;
}

void output_i32(int32_t n) {
    std::cout << n << std::endl;
}
}
