#include "finalization_test.impl.hpp"
#include "finalization_test.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

#include <iostream>

using namespace taihe;
using namespace finalization_test;

namespace {
// To be implemented.

class FooImpl {
public:
  FooImpl() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }

  ~FooImpl() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }

  void introduce() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }
};

Foo makeFoo() {
  // The parameters in the make_holder function should be of the same type
  // as the parameters in the constructor of the actual implementation class.
  return make_holder<FooImpl, Foo>();
}
}  // namespace

TH_EXPORT_CPP_API_makeFoo(makeFoo);
