#include "native_user.impl.hpp"
#include <iostream>
#include "native_user.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

namespace {
// To be implemented.

::taihe::string UseIfaceA(::impl::weak::IfaceA_taihe obj) {
  std::cout << "native call Foo(): " << obj->Foo() << std::endl;
  std::cout << "native call Bar(): " << obj->Bar() << std::endl;
  return obj->Foo();
}
}  // namespace

// Since these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_UseIfaceA(UseIfaceA);
// NOLINTEND
