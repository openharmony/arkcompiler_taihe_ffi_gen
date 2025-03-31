#include "taihe/string.hpp"

#include "stdexcept"
#include "string_io.impl.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {
string input() {
  return "input";
}

void print(string_view a) {
  std::cout << a << std::flush;
}

void println(string_view a) {
  std::cout << a << std::endl;
}
}  // namespace

TH_EXPORT_CPP_API_input(input);
TH_EXPORT_CPP_API_print(print);
TH_EXPORT_CPP_API_println(println);
