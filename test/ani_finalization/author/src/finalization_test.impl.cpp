#include "finalization_test.impl.hpp"
#include "finalization_test.proj.hpp"
#include "stdexcept"
#include "taihe/runtime.hpp"

#include <iostream>
#include <taihe/vector.hpp>

using namespace taihe;
using namespace finalization_test;

namespace {
// To be implemented.

class FooImpl {
  vector<callback<void()>> callbacks;

public:
  FooImpl() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
  }

  void addCallback(callback_view<void()> callback) {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
    callbacks.emplace_back(callback);
  }

  ~FooImpl() {
    std::cout << __PRETTY_FUNCTION__ << std::endl;
    for (callback_view<void()> callback : callbacks) {
      callback();
    }
  }
};

Foo makeFoo() {
  // The parameters in the make_holder function should be of the same type
  // as the parameters in the constructor of the actual implementation class.
  return make_holder<FooImpl, Foo>();
}
}  // namespace

// because these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_makeFoo(makeFoo);
// NOLINTEND
