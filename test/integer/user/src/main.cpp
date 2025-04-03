#include <iostream>

#include "integer.arithmetic.user.hpp"
#include "integer.io.user.hpp"

using namespace integer;

int main() {
  std::cout << "Please enter a 32-bit signed integer a: ";
  auto a = io::input_i32();
  std::cout << "Please enter a 32-bit signed integer b: ";
  auto b = io::input_i32();

  auto sum = arithmetic::add_i32(a, b);
  auto diff = arithmetic::sub_i32(a, b);
  auto prod = arithmetic::mul_i32(a, b);
  auto [quo, rem] = arithmetic::divmod_i32(a, b);

  std::cout << "a + b = ";
  io::output_i32(sum);
  std::cout << "a - b = ";
  io::output_i32(diff);
  std::cout << "a * b = ";
  io::output_i32(prod);
  std::cout << "a / b = ";
  io::output_i32(quo);
  std::cout << "a % b = ";
  io::output_i32(rem);
}
