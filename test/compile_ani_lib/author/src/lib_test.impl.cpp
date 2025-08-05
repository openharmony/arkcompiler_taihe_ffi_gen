#include "lib_test.impl.hpp"
#include <iostream>
#include "lib_test.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

namespace {
// To be implemented.

class IfaceAImpl {
public:
  IfaceAImpl() {}

  void Foo() {
    std::cout << "IfaceA::Foo" << std::endl;
  }

  void Bar() {
    std::cout << "IfaceA::Bar" << std::endl;
  }
};

::lib_test::IfaceA MakeIfaceA() {
  // The parameters in the make_holder function should be of the same type
  // as the parameters in the constructor of the actual implementation class.
  return taihe::make_holder<IfaceAImpl, ::lib_test::IfaceA>();
}

void UseIfaceA(::lib_test::weak::IfaceA obj) {
  std::cout << "UseIfaceA" << std::endl;
  obj->Foo();
  obj->Bar();
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_MakeIfaceA(MakeIfaceA);
TH_EXPORT_CPP_API_UseIfaceA(UseIfaceA);
// NOLINTEND
