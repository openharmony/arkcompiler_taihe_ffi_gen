#include "struct_extend.impl.hpp"

#include <iostream>

#include "stdexcept"
#include "struct_extend.A.proj.1.hpp"
#include "struct_extend.B.proj.1.hpp"
#include "struct_extend.C.proj.1.hpp"
#include "struct_extend.D.proj.1.hpp"
#include "struct_extend.E.proj.1.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe::core;
namespace {
void check_A(::struct_extend::A const& i) {
  std::cout << i.param1 << std::endl;
}
::struct_extend::A create_A() { return {1}; }
void check_B(::struct_extend::B const& i) {
  std::cout << i.a.param1 << std::endl;
  std::cout << i.param2 << std::endl;
}
::struct_extend::B create_B() { return {{1}, 2}; }
void check_C(::struct_extend::C const& i) {
  std::cout << i.b.a.param1 << std::endl;
  std::cout << i.b.param2 << std::endl;
  std::cout << i.param3 << std::endl;
}
::struct_extend::C create_C() { return {{{1}, 2}, 3}; }
void check_D(::struct_extend::D const& i) {
  std::cout << i.param4 << std::endl;
}
::struct_extend::D create_D() { return {4}; }
void check_E(::struct_extend::E const& i) {
  std::cout << i.d.param4 << std::endl;
  std::cout << i.param5 << std::endl;
}
::struct_extend::E create_E() { return {{4}, 5}; }
}  // namespace
TH_EXPORT_CPP_API_check_A(check_A);
TH_EXPORT_CPP_API_create_A(create_A);
TH_EXPORT_CPP_API_check_B(check_B);
TH_EXPORT_CPP_API_create_B(create_B);
TH_EXPORT_CPP_API_check_C(check_C);
TH_EXPORT_CPP_API_create_C(create_C);
TH_EXPORT_CPP_API_check_D(check_D);
TH_EXPORT_CPP_API_create_D(create_D);
TH_EXPORT_CPP_API_check_E(check_E);
TH_EXPORT_CPP_API_create_E(create_E);
