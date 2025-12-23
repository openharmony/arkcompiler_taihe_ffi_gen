#include "module1.foo.impl.hpp"
#include <iostream>
#include "module1.foo.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

using namespace taihe;

namespace {
void fooFunc() {
  std::cout << "namespace: module1.foo, func: foo" << std::endl;
}
}  // namespace

// NOLINTBEGIN
TH_EXPORT_CPP_API_fooFunc(fooFunc);
// NOLINTEND
