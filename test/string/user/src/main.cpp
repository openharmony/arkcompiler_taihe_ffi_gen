#include <iostream>

#include "string.io.abi.hpp"
#include "string.op.abi.hpp"

int main() {
    std::cout << "Please input string a: ";
    auto a = string::io::input();
    std::cout << "Please input string b: ";
    auto b = string::io::input();

    auto a_b = string::op::concat(a, b);

    std::cout << "a + b = ";
    string::io::output(a_b);

    std::cout << "Please input a number n: ";

    auto n_str = string::io::input();
    int32_t n = std::atoi(n_str.c_str());

    auto [a_0, a_1] = string::op::split(a, n);
    auto [b_0, b_1] = string::op::split(b, n);

    std::cout << "a[:n] = ";
    string::io::output(a_0);
    std::cout << "a[n:] = ";
    string::io::output(a_1);
    std::cout << "b[:n] = ";
    string::io::output(b_0);
    std::cout << "b[n:] = ";
    string::io::output(b_1);
}
