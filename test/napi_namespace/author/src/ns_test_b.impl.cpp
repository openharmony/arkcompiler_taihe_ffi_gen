#include <iostream>
#include "my_module_a.ns1.ns2.ns3.ns4.ns5.impl.hpp"
#include "my_module_a.ns1.ns2.ns3.ns4.ns5.proj.hpp"

namespace {

int32_t Funtest(::my_module_a::ns1::ns2::ns3::ns4::ns5::MyStruct const &s) {
  return s.a + s.b;
}

void foo() {
  std::cout << "namespace: my_module_a.ns1.ns2.ns3.ns4.ns5, func: noo"
            << std::endl;
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_Funtest(Funtest);
TH_EXPORT_CPP_API_foo(foo);
// NOLINTEND
