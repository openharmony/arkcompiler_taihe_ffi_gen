#include "inject_test.Foo.proj.2.hpp"
#include "inject_test.impl.hpp"
#include "stdexcept"
#include "taihe/string.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {

class Foo {
public:
  void with_this(uintptr_t thiz) {
    std::cout << thiz << std::endl;
  }
};

::inject_test::Foo makeFoo() {
  return make_holder<Foo, ::inject_test::Foo>();
}

}  // namespace

// because these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_makeFoo(makeFoo);
// NOLINTEND
