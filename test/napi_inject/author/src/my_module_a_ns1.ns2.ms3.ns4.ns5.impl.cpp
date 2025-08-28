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

::my_module_a::ns1::ns2::ns3::ns4::ns5::MyClass create_myclass(bool a,
                                                               float b) {
  return ::my_module_a::ns1::ns2::ns3::ns4::ns5::MyClass{a, b};
}

int32_t add(int32_t a, int32_t b) {
  return a + b;
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_Funtest(Funtest);
TH_EXPORT_CPP_API_foo(foo);
TH_EXPORT_CPP_API_create_myclass(create_myclass);
TH_EXPORT_CPP_API_add(add);
// NOLINTEND
