#include "integer.arithmetic.h"
#include "integer.io.h"
#include <iostream>
using namespace integer;
int main() {
    std::cout << "Please enter two 32-bit signed integers:" << std::endl;
    auto a = io::input_i32();
    auto b = io::input_i32();
    auto sum = arithmetic::add_i32(a, b);
    auto diff = arithmetic::sub_i32(a, b);
    io::output_i32(sum);
    io::output_i32(diff);
}
