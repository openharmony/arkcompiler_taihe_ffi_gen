#include <async_test.impl.hpp>
#include <cstdint>
#include <iostream>

#include "core/runtime.hpp"

int32_t add_impl(int32_t a, int32_t b) {
  if (a == 0) {
    taihe::core::throw_error("some error happen in add impl");
    return b;
  } else {
    std::cout << "add impl " << a + b << std::endl;
    return a + b;
  }
}

::async_test::IBase getIBase_impl() {
  struct AuthorIBase {
    taihe::core::string name;
    AuthorIBase() : name("My IBase") {}
    ~AuthorIBase() {}
    taihe::core::string get() { return name; }
    void set(taihe::core::string_view a) {
      this->name = a;
      return;
    }
  };
  return taihe::core::make_holder<AuthorIBase, ::async_test::IBase>();
}

void fromStructSync_impl(::async_test::Data const& data) {
  std::cout << data.a.c_str() << " " << data.b.c_str() << " " << data.c
            << std::endl;
  return;
}

::async_test::Data toStructSync_impl(taihe::core::string_view a,
                                     taihe::core::string_view b, int32_t c) {
  if (c == 0) {
    taihe::core::throw_error("some error happen in toStructSync_impl");
    return {a, b, c};
  }
  return {a, b, c};
}

TH_EXPORT_CPP_API_addSync(add_impl);
TH_EXPORT_CPP_API_getIBase(getIBase_impl);
TH_EXPORT_CPP_API_fromStructSync(fromStructSync_impl);
TH_EXPORT_CPP_API_toStructSync(toStructSync_impl);
