#include <iostream>
#include "my_module_a.ns1.impl.hpp"
#include "my_module_a.ns1.proj.hpp"

namespace {
::taihe::string Funtest(::my_module_a::ns1::Color s) {
  switch (s.get_key()) {
  case ::my_module_a::ns1::Color::key_t::BLUE:
    return "blue";
  case ::my_module_a::ns1::Color::key_t::GREEN:
    return "green";
  case ::my_module_a::ns1::Color::key_t::RED:
    return "red";
  }
  return "error";
}

void noo() {
  std::cout << "namespace: my_module_a.ns1, func: noo" << std::endl;
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_Funtest(Funtest);
TH_EXPORT_CPP_API_noo(noo);
// NOLINTEND
