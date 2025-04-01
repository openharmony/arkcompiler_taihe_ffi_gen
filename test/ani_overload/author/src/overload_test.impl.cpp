#include "overload_test.impl.hpp"

#include <iostream>

#include "stdexcept"
#include "taihe/string.hpp"
// Please delete <stdexcept> include when you implement
using namespace taihe;

namespace {

class Foo {
public:
  int32_t bar_int(int32_t a) {
    return a;
  }

  string bar_str(string_view a) {
    return a;
  }
};

int32_t add_int(int32_t a, int32_t b) {
  return a + b;
}

string add_str(string_view a, string_view b) {
  return a + b;
}

::overload_test::Foo makeFoo() {
  return make_holder<Foo, ::overload_test::Foo>();
}

}  // namespace

TH_EXPORT_CPP_API_add_int(add_int);
TH_EXPORT_CPP_API_add_str(add_str);
TH_EXPORT_CPP_API_makeFoo(makeFoo);
