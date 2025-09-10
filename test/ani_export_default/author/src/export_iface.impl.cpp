#include "export_iface.impl.hpp"
#include <iostream>
#include "export_iface.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

namespace {
// To be implemented.

class IfaceAImpl {
public:

public:
  IfaceAImpl() {}

  void Foo() {
    std::cout << "Export IfaceA Foo()" << std::endl;
  }

  void Bar() {
    std::cout << "Export IfaceA Bar()" << std::endl;
  }
};

::export_iface::IfaceA CreateIfaceA() {
  return taihe::make_holder<IfaceAImpl, ::export_iface::IfaceA>();
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_CreateIfaceA(CreateIfaceA);
// NOLINTEND
