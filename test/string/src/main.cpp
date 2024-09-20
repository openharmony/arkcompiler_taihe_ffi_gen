#include <iostream>

#include "string.io.abi.hpp"
#include "string.op.abi.hpp"

int main() {
    auto a = string::io::input();
    auto b = string::io::input();
    auto c = string::op::concat(a, b);
    auto d = string::op::concat(b, a);
    string::io::output(c);
    string::io::output(d);
}
