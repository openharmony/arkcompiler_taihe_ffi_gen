#include <cstdint>
#include "inject_test.Foo.proj.2.hpp"
#include "inject_test.impl.hpp"
#include "stdexcept"
#include "taihe/string.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {

class Foo {
public:
  void CallWithThis(uintptr_t thiz) {
    std::cout << thiz << std::endl;
  }
};

::inject_test::Foo MakeFooWithThis(uintptr_t thiz) {
  std::cout << thiz << std::endl;
  return make_holder<Foo, ::inject_test::Foo>();
}

}  // namespace

// because these macros are auto-generate, lint will cause false positive.
// NOLINTBEGIN
TH_EXPORT_CPP_API_MakeFooWithThis(MakeFooWithThis);
// NOLINTEND
